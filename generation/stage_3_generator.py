import numpy as np
from collections import deque
from utils.colour_utils import generate_color_map
from utils.config import REGION_BASE_TRAVERSAL_COST, STEEPNESS_MULTIPLIER

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

    region_map = np.empty((rows, cols), dtype="<U20")
    fertility_map = np.zeros((rows, cols), dtype=float)
    traversal_cost_map = np.zeros((rows, cols), dtype=float)


    for r in range(rows):
        for c in range(cols):
            region_map[r][c] = determine_region(region_conditions, elevation_map[r][c], temperature_map[r][c], rainfall_map[r][c], sea_proximity_map[r][c], river_proximity_map[r][c])
            fertility_map[r][c] = calculate_soil_fertility(rainfall_map[r][c], elevation_map[r][c])
            traversal_cost_map[r][c] = calculate_traversal_cost(region_map[r][c], steepness_map[r][c], sea_map[r][c], river_map[r][c])
            
    logging.debug(f"Biome classification took {time.time() - start_time:.2f} seconds")


    return river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map





### **Traversal & Environmental Calculations**
def calculate_traversal_cost(region, steepness, sea, river):
    """
    Determines the movement difficulty of a terrain tile.
    Higher values indicate slower movement.
    """
    return REGION_BASE_TRAVERSAL_COST.get(region, 1) + (steepness * STEEPNESS_MULTIPLIER)




def calculate_soil_fertility(rainfall, elevation):
    """
    Determines soil fertility based on rainfall and elevation.
    """
    if elevation > 0.7:
        fertility = 0.1 * rainfall  # High mountains have poor fertility
    elif elevation < 0.2:
        fertility = rainfall * 1.2  # Lowlands near water are highly fertile
    else:
        fertility = rainfall

    return normalize(fertility, 0, 1)


def determine_region(region_conditions, elevation, temperature, rainfall, sea_proximity, river_proximity):
    """
    Assigns a biome based on environmental conditions.
    """
    if sea_proximity == 0 or river_proximity == 0:
        return "water"

    for condition in region_conditions:
        if condition["condition"](elevation, temperature, rainfall, river_proximity):
            return condition["color"]

    return "grassland"  # Default biome


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
