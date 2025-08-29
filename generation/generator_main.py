from generation.stage_1_generator import generate_stage_1
from generation.stage_2_generator import generate_stage_2
from generation.stage_3_generator import generate_stage_3
from extras.stage_4_generator import generate_stage_4, update_population

import numpy as np
import time
import logging
import utils.config as config

logging.basicConfig(level=logging.DEBUG)


def generate_static_maps():
    start_time = time.time()
    elevation_map, rainfall_map, temperature_map = generate_stage_1(config.WORLD_ROWS, config.WORLD_COLS, config.SCALE, config.SEED)
    logging.debug(f"Stage 1 generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_map, sea_map, steepness_map = generate_stage_2(config.WORLD_ROWS, config.WORLD_COLS, config.NUMBER_OF_RIVERS, config.SEA_LEVEL, elevation_map, config.RIVER_SOURCE_MIN_ELEVATION)
    logging.debug(f"Stage 2 generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map, desiribility_map = generate_stage_3(config.WORLD_ROWS, config.WORLD_COLS, river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map, config.REGION_CONDITIONS, config.REGION_COLORS, config.REGIONS_TO_BLEND)
    logging.debug(f"Stage 3 generation took {time.time() - start_time:.2f} seconds")

    static_float_layers_index = {
        'desiribility': 0,
        'elevation': 1,
        'traversal_cost': 2,
        'steepness': 3,
    }

    static_float_layers = np.zeros((len(static_float_layers_index), config.WORLD_ROWS, config.WORLD_COLS), dtype=np.float32)


    static_float_layers[static_float_layers_index['desiribility']] = desiribility_map
    static_float_layers[static_float_layers_index['elevation']] = elevation_map
    static_float_layers[static_float_layers_index['traversal_cost']] = traversal_cost_map
    static_float_layers[static_float_layers_index['steepness']] = steepness_map

    static_int_layers_index = {
        'region': 0,
        'river': 1,
        'sea': 2,
    }

    static_int_layers = np.zeros((len(static_int_layers_index), config.WORLD_ROWS, config.WORLD_COLS), dtype=np.uint8)

    static_int_layers[static_int_layers_index['river']] = river_map.astype(np.uint8)
    static_int_layers[static_int_layers_index['sea']] = sea_map.astype(np.uint8)

    # Create a lookup table for region names to region ID
    region_lookup = {region: idx for idx, region in enumerate(config.REGION_COLORS.keys())}

    #This code increased peak memory usage significantly, below method is much more effective
    #static_int_layers[static_int_layers_index['region']] = np.vectorize(region_lookup.get)(region_map).astype(np.uint8)

    region_map_int = np.zeros_like(region_map, dtype=np.uint8)
    for region_name, idx in region_lookup.items():
        region_map_int[region_map == region_name] = idx
    static_int_layers[static_int_layers_index['region']] = region_map_int


    static_layers_dict = {}

    # Add float layers
    for name, idx in static_float_layers_index.items():
        static_layers_dict[name] = static_float_layers[idx]

    # Add int layers
    for name, idx in static_int_layers_index.items():
        static_layers_dict[name] = static_int_layers[idx]

    return static_layers_dict



def generate_dynamic_maps(static_data):
    population_map = generate_stage_4(static_data['desiribility'])

    dynamic_float_layers_index = {
        'population': 0,
    }

    dynamic_float_layers = np.zeros((len(dynamic_float_layers_index), config.WORLD_ROWS, config.WORLD_COLS), dtype=np.float32)

    dynamic_float_layers[dynamic_float_layers_index['population']] = population_map

    dynamic_layers_dict = {}

    for name, idx in dynamic_float_layers_index.items():
        dynamic_layers_dict[name] = dynamic_float_layers[idx]
    
    return dynamic_layers_dict

def update_dynamic_maps(static_data, dynamic_data):
    population_map = update_population(static_data['desiribility'], dynamic_data['population'])
    
    dynamic_data['population'] = population_map

    return dynamic_data
