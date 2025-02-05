from stage_1_generator import generate_stage_1
from stage_2_generator import generate_stage_2
from stage_3_generator import generate_stage_3
from stage_4_generator import generate_stage_4
from stage_5_generator import generate_stage_5
from stage_6_generator import generate_stage_6
import time
import logging
import config

logging.basicConfig(level=logging.DEBUG)


def generate_initial_maps():
    start_time = time.time()
    elevation_map, rainfall_map, temperature_map = generate_stage_1(config.ROWS, config.COLS, config.SCALE, config.SEED)
    logging.debug(f"Stage 1 generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_map, sea_map, steepness_map = generate_stage_2(config.ROWS, config.COLS, config.NUMBER_OF_RIVERS, config.SEA_LEVEL, elevation_map, config.RIVER_SOURCE_MIN_ELEVATION)
    logging.debug(f"Stage 2 generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map, colour_map, desiribility_map = generate_stage_3(config.ROWS, config.COLS, river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map, config.REGION_CONDITIONS, config.REGION_COLORS, config.REGIONS_TO_BLEND)
    logging.debug(f"Stage 3 generation took {time.time() - start_time:.2f} seconds")

    #start_time = time.time()
    #population_map = generate_stage_4(desiribility_map)
    #logging.debug(f"Stage 4 generation took {time.time() - start_time:.2f} seconds")
    
    #start_time = time.time()
    #cities_map, cities_list = generate_stage_5(population_map, config.NUMBER_OF_CITIES)
    #logging.debug(f"Stage 5 generation took {time.time() - start_time:.2f} seconds")
    
    #start_time = time.time()
    #traversal_cost_multiplier_map, colour_map_with_paths = generate_stage_6(cities_list, traversal_cost_map, colour_map)
    #logging.debug(f"Stage 6 generation took {time.time() - start_time:.2f} seconds")

    #colour_map_with_paths[cities_map] = (0,0,0)

    return colour_map, desiribility_map, elevation_map, traversal_cost_map, sea_map, river_map, steepness_map