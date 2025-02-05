import numpy as np
from collections import deque
from colour_generator import generate_color_map
from config import REGION_BASE_TRAVERSAL_COST, STEEPNESS_MULTIPLIER
import logging
import time

def generate_stage_3(rows, cols, river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map, region_conditions, region_colours, regions_to_blend):
    river_proximity_map = np.zeros((rows, cols), dtype=int)
    sea_proximity_map = np.zeros((rows, cols), dtype=int)
    region_map = np.zeros((rows, cols), dtype='<U20')
    fertility_map = np.zeros((rows, cols), dtype=float)
    traversal_cost_map = np.zeros((rows, cols), dtype=float)
    colour_map = np.zeros((rows, cols, 3), dtype=np.uint8)
    desiribility_map = np.zeros((rows, cols), dtype=float)

    river_proximity_map = calculate_proximity_map(river_map)
    sea_proximity_map = calculate_proximity_map(sea_map)


    for r in range(rows):
        for c in range(cols):
            region_map[r][c] = determine_region(region_conditions, elevation_map[r][c], temperature_map[r][c], rainfall_map[r][c], sea_proximity_map[r][c], river_proximity_map[r][c])
            fertility_map[r][c] = calculate_soil_fertility(rainfall_map[r][c], elevation_map[r][c])
            traversal_cost_map[r][c] = calculate_traversal_cost(region_map[r][c], steepness_map[r][c], sea_map[r][c], river_map[r][c])
            desiribility_map[r][c] = calculate_desirability(fertility_map[r][c], temperature_map[r][c], river_proximity_map[r][c], sea_map[r][c], river_map[r][c])
    

    start_time = time.time()
    colour_map = generate_color_map(elevation_map, steepness_map, region_map, region_colours, regions_to_blend, True, True)
    logging.debug(f"Colour took {time.time() - start_time:.2f} seconds")
        
    return river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map, colour_map, desiribility_map


def calculate_traversal_cost(region, steepness, sea, river):
    return REGION_BASE_TRAVERSAL_COST[region] + (steepness*STEEPNESS_MULTIPLIER)


def calculate_desirability(fertility, temperature, proximity_to_water, sea, river, water_threshold=5):
    """
    Calculate desirability based on fertility, temperature, and proximity to water.
    Normalized to the range [0, 1].
    
    Parameters:
    - fertility: Fertility factor of the land.
    - temperature: Temperature factor (normalized to [0,1]).
    - proximity_to_water: Distance to the nearest water source.
    - water_threshold: Distance below which desirability increases.
    
    Returns:
    - Normalized desirability value in the range [0,1].
    """
    min_desirability, max_desirability = 0, 1

    if sea or river:
        return 0

    # Temperature factor - best temperature around 0.5, less desirable if too hot or cold
    if temperature < 0.0 or temperature > 1:
        temp_factor = 0.5  # Penalize extreme temperatures
    else:
        temp_factor = 1 - abs(0.5 - temperature)  # More desirable around 0.5

    # Base desirability calculation
    desirability = fertility * temp_factor

    # Modify desirability based on proximity to water
    if proximity_to_water < water_threshold:
        water_bonus = (water_threshold - proximity_to_water) / water_threshold  # Closer = higher bonus
        desirability += water_bonus * 0.3  # Weight of water influence

    # Normalize the result within the desirability range
    return normalize(round(desirability, 2), min_desirability, max_desirability)


def calculate_soil_fertility(rainfall, elevation):
    """
    Calculate soil fertility based on rainfall and elevation, normalized to [0, 1].
    """
    min_fertility, max_fertility = 0, 1

    if elevation > 0.7:  # Very high elevations are less fertile
        fertility = 0.1 * rainfall
    elif elevation < 0.2:  # Lowlands near water are highly fertile
        fertility = rainfall * 1.2
    else:
        fertility = rainfall  # Moderate fertility otherwise

    return normalize(fertility, min_fertility, max_fertility)


def determine_region(region_conditions, elevation, temperature, rainfall, sea_proximity, river_proximity):
    if sea_proximity == 0 or river_proximity == 0:
        return "water"
    for condition in region_conditions:
        if condition["condition"](elevation, temperature, rainfall, river_proximity):
            return condition["color"]


def calculate_proximity_map(boolean_map):
    rows, cols = len(boolean_map), len(boolean_map[0])
    
    # Initialize the proximity map with a large value for unvisited cells
    proximity_map = [[float('inf')] * cols for _ in range(rows)]
    
    # Queue to store river cells (starting points for BFS)
    queue = deque()
    
    # Initialize the proximity map and queue with True positions
    for r in range(rows):
        for c in range(cols):
            if boolean_map[r][c] == 1:  
                proximity_map[r][c] = 0
                queue.append((r, c))

    # Directions for 4-way movement (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # BFS to calculate shortest distance to True value
    while queue:
        r, c = queue.popleft()
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            # Ensure within map bounds
            if 0 <= nr < rows and 0 <= nc < cols:
                
                # If new distance is shorter, update and enqueue
                if proximity_map[nr][nc] > proximity_map[r][c] + 1:
                    proximity_map[nr][nc] = proximity_map[r][c] + 1
                    queue.append((nr, nc))
    
    # Replace float('inf') with -1 for unreachable cells
    for r in range(rows):
        for c in range(cols):
            if proximity_map[r][c] == float('inf'):
                proximity_map[r][c] = -1
    
    return proximity_map

def normalize(value, min_value, max_value):
    """
    Normalize a value to the range [0, 1].
    """
    return (value - min_value) / (max_value - min_value)
