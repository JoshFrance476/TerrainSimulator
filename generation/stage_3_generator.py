import numpy as np
from config import STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST, REGION_COST_LOOKUP, REGION_RULES, REGION_NAME_TO_ID
from utils.map_utils import calculate_proximity_map


def generate_stage_3(river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map):

    river_proximity_map = calculate_proximity_map(river_map)
    sea_proximity_map = calculate_proximity_map(sea_map)

    region_map = determine_region(elevation_map, temperature_map, rainfall_map, sea_proximity_map, river_proximity_map)
    fertility_map = calculate_soil_fertility(region_map, rainfall_map, elevation_map, temperature_map)
    traversal_cost_map = calculate_traversal_cost(region_map, steepness_map)            

    return river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map





def calculate_traversal_cost(region_map, steepness_map):
    cost_lookup = REGION_COST_LOOKUP[region_map]

    steepness_cost = steepness_map * STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST
    traversal_cost_map = cost_lookup + steepness_cost

    return traversal_cost_map




def calculate_soil_fertility(region, rainfall, elevation, temperature):
    """
    Determines soil fertility based on rainfall, elevation, temperature and region.
    """
    fertility = rainfall.copy()

    fertility[elevation > 0.7] *= 0.1
    fertility[elevation < 0.2] *= 1.2

    fertility[region == REGION_NAME_TO_ID['ocean']] = 0
    fertility[region == REGION_NAME_TO_ID['desert']] *= 0.1
    fertility[region == REGION_NAME_TO_ID['arid']] *= 0.4
    fertility[region == REGION_NAME_TO_ID['mountains']] *= 0.1
    fertility[region == REGION_NAME_TO_ID['snowy peaks']] *= 0.05
    fertility[region == REGION_NAME_TO_ID['marsh']] *= 0.5
    fertility[region == REGION_NAME_TO_ID['savanna']] *= 0.5
    fertility[region == REGION_NAME_TO_ID['grassland']] *= 1.2



    weight = 1.0 - (temperature - 0.5)**2 * 4
    weight = np.clip(weight, 0, 1)   
    fertility *= weight

    min_val = fertility.min()
    max_val = fertility.max()
    fertility = (fertility - min_val) / (max_val - min_val + 1e-9)

    return fertility




def determine_region(elevation, temperature, rainfall, sea_proximity, river_proximity):
    region_map = np.full(elevation.shape, -1, dtype=np.int8)
    factors = {
        "elevation": elevation,
        "temperature": temperature,
        "rainfall": rainfall,
        "river_proximity": river_proximity,
        "sea_proximity": sea_proximity
    }

    river_mask = (river_proximity == 0)
    region_map[river_mask] = REGION_NAME_TO_ID['river']


    for region_data in REGION_RULES:
        option_masks = []  # collect masks for each option in the list
        if "conditions" in region_data:
            for option in region_data["conditions"]:   # each option is a dict
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
            region_map[(region_map == -1) & combined_mask] = REGION_NAME_TO_ID[region_data["name"]]

    return region_map





