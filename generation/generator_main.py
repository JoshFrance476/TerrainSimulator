from generation.stage_1_generator import generate_stage_1
from generation.stage_2_generator import generate_stage_2
from generation.stage_3_generator import generate_stage_3
from generation.stage_4_generator import generate_stage_4

import numpy as np
import time
import logging
import utils.config as config

logging.basicConfig(level=logging.DEBUG)




def generate_static_maps(rows, cols):
    start_time = time.time()
    elevation_map, rainfall_map, temperature_map = generate_stage_1(rows, cols, config.SCALE, config.SEED)
    logging.debug(f"Stage 1 generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_map, sea_map, steepness_map, coastline_map = generate_stage_2(config.NUMBER_OF_RIVERS, config.SEA_LEVEL, elevation_map, config.RIVER_SOURCE_MIN_ELEVATION)
    logging.debug(f"Stage 2 generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map = generate_stage_3(river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map, config.REGION_CONDITIONS)
    logging.debug(f"Stage 3 generation took {time.time() - start_time:.2f} seconds")

    
    return elevation_map, rainfall_map, temperature_map, river_map, sea_map, steepness_map, coastline_map, river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map   






def generate_dynamic_maps(static_data):
    start_time = time.time()
    population_capacity_map, population_map, resource_map = generate_stage_4(static_data)
    logging.debug(f"Stage 4 generation took {time.time() - start_time:.2f} seconds")

    return population_capacity_map, population_map, resource_map


#def update_dynamic_maps(static_data, dynamic_data):
