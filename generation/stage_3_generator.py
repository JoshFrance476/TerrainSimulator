import numpy as np
from utils.config import REGION_BASE_TRAVERSAL_COST, STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST, REGION_LOOKUP
from utils.map_utils import calculate_proximity_map


def generate_stage_3(river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map, region_conditions):

    river_proximity_map = calculate_proximity_map(river_map)
    sea_proximity_map = calculate_proximity_map(sea_map)

    region_map = determine_region(region_conditions, elevation_map, temperature_map, rainfall_map, sea_proximity_map, river_proximity_map)
    fertility_map = calculate_soil_fertility(region_map, rainfall_map, elevation_map, temperature_map)
    traversal_cost_map = calculate_traversal_cost(region_map, steepness_map)            

    return river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map





def calculate_traversal_cost(region_map, steepness_map):
    base_cost = REGION_BASE_TRAVERSAL_COST[region_map]
    steepness_cost = steepness_map * STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST
    traversal_cost_map = base_cost + steepness_cost

    return traversal_cost_map




def calculate_soil_fertility(region, rainfall, elevation, temperature):
    """
    Determines soil fertility based on rainfall, elevation, temperature and region.
    """
    fertility = rainfall.copy()

    fertility[elevation > 0.7] *= 0.1
    fertility[elevation < 0.2] *= 1.2

    fertility[region == REGION_LOOKUP['water']] = 0
    fertility[region == REGION_LOOKUP['desert']] *= 0.1
    fertility[region == REGION_LOOKUP['arid']] *= 0.4
    fertility[region == REGION_LOOKUP['mountains']] *= 0.1
    fertility[region == REGION_LOOKUP['snowy peaks']] *= 0.05
    fertility[region == REGION_LOOKUP['marsh']] *= 0.5
    fertility[region == REGION_LOOKUP['savanna']] *= 0.5
    fertility[region == REGION_LOOKUP['grassland']] *= 1.2



    weight = 1.0 - (temperature - 0.5)**2 * 4
    weight = np.clip(weight, 0, 1)   
    fertility *= weight

    min_val = fertility.min()
    max_val = fertility.max()
    fertility = (fertility - min_val) / (max_val - min_val + 1e-9)

    return fertility




def determine_region(region_conditions, elevation, temperature, rainfall, sea_proximity, river_proximity):
    region_map = np.full(elevation.shape, -1, dtype=np.int8)

    water_mask = (sea_proximity == 0) | (river_proximity == 0)

    region_map = np.where(water_mask, REGION_LOOKUP["water"], region_map)
    for condition in region_conditions:
        mask = condition["condition"](elevation, temperature, rainfall, river_proximity)
        region_map = np.where((region_map == -1) & mask,
                              condition["regionID"], region_map)

    return region_map


