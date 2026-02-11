import numpy as np
from config import STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST, BIOME_COST_LOOKUP, BIOME_RULES, BIOME_NAME_TO_ID
from utils.map_utils import calculate_proximity_map


def calculate_traversal_cost(biome_map, steepness_map):
    cost_lookup = BIOME_COST_LOOKUP[biome_map]

    steepness_cost = steepness_map * STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST
    traversal_cost_map = cost_lookup + steepness_cost

    return traversal_cost_map


def calculate_soil_fertility(biome, rainfall, elevation, temperature):
    """
    Determines soil fertility based on rainfall, elevation, temperature and biome.
    """
    fertility = rainfall.copy()

    fertility[elevation > 0.7] *= 0.1
    fertility[elevation < 0.2] *= 1.2

    fertility[biome == BIOME_NAME_TO_ID['ocean']] = 0
    fertility[biome == BIOME_NAME_TO_ID['desert']] *= 0.1
    fertility[biome == BIOME_NAME_TO_ID['arid']] *= 0.4
    fertility[biome == BIOME_NAME_TO_ID['mountains']] *= 0.1
    fertility[biome == BIOME_NAME_TO_ID['snowy peaks']] *= 0.05
    fertility[biome == BIOME_NAME_TO_ID['marsh']] *= 0.5
    fertility[biome == BIOME_NAME_TO_ID['savanna']] *= 0.5
    fertility[biome == BIOME_NAME_TO_ID['grassland']] *= 1.2



    weight = 1.0 - (temperature - 0.5)**2 * 4
    weight = np.clip(weight, 0, 1)   
    fertility *= weight

    min_val = fertility.min()
    max_val = fertility.max()
    fertility = (fertility - min_val) / (max_val - min_val + 1e-9)

    return fertility




def determine_biome(elevation, temperature, rainfall, sea_proximity, river_proximity):
    biome_map = np.full(elevation.shape, -1, dtype=np.int8)
    factors = {
        "elevation": elevation,
        "temperature": temperature,
        "rainfall": rainfall,
        "river_proximity": river_proximity,
        "sea_proximity": sea_proximity
    }

    river_mask = (river_proximity == 0)
    biome_map[river_mask] = BIOME_NAME_TO_ID['river']


    for biome_data in BIOME_RULES:
        option_masks = []  # collect masks for each option in the list
        if "conditions" in biome_data:
            for option in biome_data["conditions"]:   # each option is a dict
                m = np.ones_like(elevation, dtype=bool)
                for factor, limits in option.items():
                    arr = factors[factor]
                    if "min" in limits:
                        m &= arr >= limits["min"]
                    if "max" in limits:
                        m &= arr <= limits["max"]
                option_masks.append(m)

        if option_masks:
            # OR together the option masks (any of the dicts can match)
            combined_mask = np.logical_or.reduce(option_masks)
            # Only fill unassigned cells
            biome_map[(biome_map == -1) & combined_mask] = BIOME_NAME_TO_ID[biome_data["name"]]

    return biome_map





