from utils.colour_utils import generate_color_map

import numpy as np
import time
import logging
import config

from utils.map_utils import generate_perlin_noise_map
from generation.stage_1_generator import calculate_temperature
from generation.stage_2_generator import calculate_steepness, generate_sea_map, generate_rivers_map
from generation.stage_3_generator import calculate_proximity_map, determine_biome, calculate_traversal_cost

if config.LOGGING:
    logging.basicConfig(level=logging.DEBUG)


def generate_data_maps(rows, cols, biome_config):

    ## Stage 1

    start_time = time.time()
    elevation_map = generate_perlin_noise_map(rows, cols, config.SCALE*1.3, config.SEED, False, 8, 0.38, 3.3)     
    logging.debug(f"Elevation map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    rainfall_map = generate_perlin_noise_map(rows, cols, config.SCALE*2, config.SEED*2, True, 5, 0.5, 2.2)    
    logging.debug(f"Rainfall map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    temperature_map = calculate_temperature(elevation_map, rows) 
    logging.debug(f"Temperature map generation took {time.time() - start_time:.2f} seconds")

    ## Stage 2

    start_time = time.time()
    sea_map = generate_sea_map(elevation_map, biome_config.constants["SEA_LEVEL"])
    logging.debug(f"Sea map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_map = generate_rivers_map(elevation_map, biome_config.constants["SEA_LEVEL"], biome_config.constants["RIVER_SOURCE_MIN_ELEVATION"], biome_config.constants["NUMBER_OF_RIVERS"])
    logging.debug(f"River map generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    steepness_map = calculate_steepness(elevation_map)
    logging.debug(f"Steepness map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_proximity_map = calculate_proximity_map(river_map)
    logging.debug(f"River proximity map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    sea_proximity_map = calculate_proximity_map(sea_map)
    logging.debug(f"Sea proximity map generation took {time.time() - start_time:.2f} seconds")

    ## Stage 3

    start_time = time.time()
    biome_map = determine_biome(elevation_map, temperature_map, rainfall_map, sea_proximity_map, river_proximity_map, biome_config)
    logging.debug(f"biome map generation took {time.time() - start_time:.2f} seconds")


    start_time = time.time()
    traversal_cost_map = calculate_traversal_cost(biome_map, steepness_map, biome_config.cost_lookup)  
    logging.debug(f"Traversal cost map generation took {time.time() - start_time:.2f} seconds")


    start_time = time.time()
    colour_map = generate_color_map({
        'elevation': elevation_map,
        'biome': biome_map,
        'steepness': steepness_map
    },
    biome_config,
    True, True)
    logging.debug(f"Colour map generation took {time.time() - start_time:.2f} seconds")

    world_data = {
        'colour': colour_map,

        #np.float32 maps
        'elevation': elevation_map,
        'temperature': temperature_map,
        'rainfall': rainfall_map,
        'traversal_cost': traversal_cost_map,
        'steepness': steepness_map,
        
        #np.uint8 maps
        'biome': biome_map,
        'river_proximity': river_proximity_map,
        'sea_proximity': sea_proximity_map,

        #np.int32 maps
        'state': np.full((rows, cols), 255, dtype=np.int32),
        'settlement_distance': np.full((rows, cols), 0, dtype=np.int32),
        'neighbour_counts': np.full((rows, cols), 255, dtype=np.int32),

        #bool maps
        'river': river_map,
        'sea': sea_map,
    
        }
    
    return world_data


def update_stage_3(elevation_map, biome_map, steepness_map, biome_config):
    traversal_cost_map = calculate_traversal_cost(biome_map, steepness_map, biome_config.cost_lookup)  

    colour_map = generate_color_map({
        'elevation': elevation_map,
        'biome': biome_map,
        'steepness': steepness_map
    },
    biome_config,
    True, True)

    return traversal_cost_map, colour_map


