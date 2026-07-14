import numpy as np
from config import STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST
from backend.generation.map_utils import calculate_proximity_map


def calculate_traversal_cost(biome_map, steepness_map, biome_cost_lookup):
    cost_lookup = biome_cost_lookup[biome_map]

    steepness_cost = steepness_map * STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST
    traversal_cost_map = cost_lookup + steepness_cost

    return traversal_cost_map


def calculate_soil_fertility(biome, rainfall, elevation, temperature, biome_config):
    """
    Determines soil fertility based on rainfall, elevation, temperature and biome.
    """
    fertility = rainfall.copy()

    fertility[elevation > 0.7] *= 0.1
    fertility[elevation < 0.2] *= 1.2

    fertility[biome == biome_config.name_to_id['ocean']] = 0
    fertility[biome == biome_config.name_to_id['desert']] *= 0.1
    fertility[biome == biome_config.name_to_id['arid']] *= 0.4
    fertility[biome == biome_config.name_to_id['mountains']] *= 0.1
    fertility[biome == biome_config.name_to_id['snowy peaks']] *= 0.05
    fertility[biome == biome_config.name_to_id['marsh']] *= 0.5
    fertility[biome == biome_config.name_to_id['savanna']] *= 0.5
    fertility[biome == biome_config.name_to_id['grassland']] *= 1.2



    weight = 1.0 - (temperature - 0.5)**2 * 4
    weight = np.clip(weight, 0, 1)   
    fertility *= weight

    min_val = fertility.min()
    max_val = fertility.max()
    fertility = (fertility - min_val) / (max_val - min_val + 1e-9)

    return fertility


def determine_biome(elevation, temperature, rainfall, sea_proximity, river_proximity, biome_config, mask=None, biome_map=None):
    # Thanks ChatGPT. Uses the old function but with an optional mask and biome_map. 
    # If provided, only determines biome within the mask and keeps the rest of biome_map the same
    
    if mask is None:
        mask = np.ones_like(elevation, dtype=bool)
    else:
        mask = (np.asarray(mask) != 0)
        if mask.shape != elevation.shape:
            raise ValueError(f"mask.shape {mask.shape} must match elevation.shape {elevation.shape}")

    if biome_map is None:
        biome_map = np.full(elevation.shape, -1, dtype=np.int16)
    else:
        if biome_map.shape != elevation.shape:
            raise ValueError("biome_map must match elevation shape")

    factors = {
        "elevation": elevation,
        "temperature": temperature,
        "rainfall": rainfall,
        "river_proximity": river_proximity,
        "sea_proximity": sea_proximity,
    }

    writable = mask
    written = np.zeros_like(mask, dtype=bool)  # track what we set this call (within mask)

    # River override (highest priority)
    river_mask = writable & (river_proximity == 0)
    biome_map[river_mask] = biome_config.name_to_id["river"]
    written |= river_mask

    for biome_data in biome_config.biomes:
        option_masks = []
        for option in biome_data.get("conditions", []):
            m = np.ones_like(elevation, dtype=bool)
            for factor, limits in option.items():
                arr = factors[factor]
                if "min" in limits:
                    m &= arr >= limits["min"]
                if "max" in limits:
                    m &= arr <= limits["max"]
            option_masks.append(m)

        if option_masks:
            combined_mask = np.logical_or.reduce(option_masks)

            # assign within mask, but don't overwrite something we've already written this call
            assign_mask = writable & ~written & combined_mask
            biome_map[assign_mask] = biome_config.name_to_id[biome_data["name"]]
            written |= assign_mask

    return biome_map





