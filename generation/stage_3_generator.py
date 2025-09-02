import numpy as np
from collections import deque
from utils.colour_utils import generate_color_map
from utils.config import REGION_BASE_TRAVERSAL_COST, STEEPNESS_MULTIPLIER, REGION_LOOKUP

import logging
import time

def generate_stage_3(rows, cols, river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map, region_conditions, region_colours, regions_to_blend):
    """
    Generates biome information, traversal costs, and desirability based on environmental conditions.
    
    Returns:
        - river_proximity_map: Distance to rivers
        - sea_proximity_map: Distance to the sea
        - region_map: Assigned biomes for each cell
        - fertility_map: Soil fertility based on elevation & rainfall
        - traversal_cost_map: Movement difficulty for AI & pathfinding
        - colour_map: Rendered map with blended biome colors
        - desirability_map: Suitable locations for settlements
    """
    start_time = time.time()

    river_proximity_map = calculate_proximity_map(river_map)
    sea_proximity_map = calculate_proximity_map(sea_map)



    region_map = determine_region(region_conditions, elevation_map, temperature_map, rainfall_map, sea_proximity_map, river_proximity_map)
    fertility_map = calculate_soil_fertility(region_map, rainfall_map, elevation_map, temperature_map)
    traversal_cost_map = calculate_traversal_cost(region_map, steepness_map, sea_map, river_map)
            


    return river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map





def calculate_traversal_cost(region_map, steepness_map, sea, river):
    base_cost = REGION_BASE_TRAVERSAL_COST[region_map]
    steepness_cost = steepness_map * STEEPNESS_MULTIPLIER
    traversal_cost_map = base_cost + steepness_cost

    return traversal_cost_map




def calculate_soil_fertility(region, rainfall, elevation, temperature):
    """
    Determines soil fertility based on rainfall and elevation.
    """

    fertility = np.where(elevation > 0.7, 0.1 * rainfall,
                np.where(elevation < 0.2, rainfall * 1.2,
                         rainfall))

    fertility = np.where(region == REGION_LOOKUP["water"], 0, fertility)
    fertility = np.where(region == REGION_LOOKUP["desert"], fertility * 0.2, fertility)
    fertility = np.where(region == REGION_LOOKUP["arid"], fertility * 0.5, fertility)    


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



### **Proximity Calculations (Water & Rivers)**
def calculate_proximity_map(boolean_map):
    """
    Calculates proximity to rivers or the sea using a breadth-first search (BFS).
    """
    rows, cols = boolean_map.shape
    proximity_map = np.full((rows, cols), float("inf"))  # Initialize with high values
    queue = deque()

    for r in range(rows):
        for c in range(cols):
            if boolean_map[r, c]:  # If it's a water tile
                proximity_map[r, c] = 0
                queue.append((r, c))

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 4-way movement

    while queue:
        r, c = queue.popleft()

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if proximity_map[nr, nc] > proximity_map[r, c] + 1:
                    proximity_map[nr, nc] = proximity_map[r, c] + 1
                    queue.append((nr, nc))

    proximity_map[proximity_map == float("inf")] = -1  # Mark unreachable areas
    return proximity_map


### **Helper Function: Normalize Values**
def normalize(value, min_value, max_value):
    """
    Normalizes a value into the range [0, 1].
    """
    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0
