from generation.stage_1_generator import generate_stage_1
from generation.stage_2_generator import generate_stage_2
from generation.stage_3_generator import generate_stage_3
from generation.stage_4_generator import generate_stage_4
from utils.colour_utils import generate_color_map
from utils.map_utils import produce_landmass_label_map, produce_label_dict, produce_continent_label_map, produce_ocean_label_map, produce_water_body_label_map

import numpy as np
import time
import logging
import config as config

logging.basicConfig(level=logging.DEBUG)


def generate_data_maps(rows, cols):
    start_time = time.time()
    elevation_map, rainfall_map, temperature_map = generate_stage_1(rows, cols, config.SCALE, config.SEED)
    logging.debug(f"Stage 1 generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_map, sea_map, steepness_map, coastline_map = generate_stage_2(config.NUMBER_OF_RIVERS, config.SEA_LEVEL, elevation_map, config.RIVER_SOURCE_MIN_ELEVATION)
    logging.debug(f"Stage 2 generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map = generate_stage_3(river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map)
    logging.debug(f"Stage 3 generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    population_capacity_map, population_map, resource_map = generate_stage_4(fertility_map, temperature_map, river_proximity_map, sea_map, river_map, elevation_map, region_map, rainfall_map)
    logging.debug(f"Stage 4 generation took {time.time() - start_time:.2f} seconds")


    colour_map = generate_color_map({
        'elevation': elevation_map,
        'region': region_map,
        'steepness': steepness_map
    }, True, True)

    water_body_label_map = produce_water_body_label_map(sea_map)

    ocean_label_map = produce_ocean_label_map(water_body_label_map)

    landmass_label_map = produce_landmass_label_map(~sea_map, ocean_label_map)

    continent_label_map, test_map = produce_continent_label_map(landmass_label_map)
    land_feature_label_map = np.zeros_like(sea_map)



    water_feature_label_map = np.zeros_like(sea_map)

    world_data = {
        'colour': colour_map,

        #np.float32 maps
        'elevation': elevation_map,
        'temperature': temperature_map,
        'rainfall': rainfall_map,
        'traversal_cost': traversal_cost_map,
        'steepness': steepness_map,
        'fertility': fertility_map,
        'population': population_map,
        'population_capacity': population_capacity_map,
        'flip_probability': np.zeros((rows, cols), dtype=np.float32),
        'decay_probability': np.zeros((rows, cols), dtype=np.float32),
        
        #np.uint8 maps
        'region': region_map,
        'river_proximity': river_proximity_map,
        'sea_proximity': sea_proximity_map,
        'coastline': coastline_map,
        'resource': resource_map,

        #np.int32 maps
        'state': np.full((rows, cols), 255, dtype=np.int32),
        'settlement_distance': np.full((rows, cols), 0, dtype=np.int32),
        'neighbour_counts': np.full((rows, cols), 255, dtype=np.int32),

        #bool maps
        'river': river_map,
        'sea': sea_map,
        
        #label maps
        'landmass_label': landmass_label_map,
        'continent_label': continent_label_map,
        'land_feature_label': test_map,
        'water_body_label': water_body_label_map,
        'ocean_label': ocean_label_map,
        'water_feature_label': water_feature_label_map
        }

    
    return world_data

def generate_label_lookups(landmass_label_map, continent_label_map, land_feature_label_map, water_body_label_map, ocean_label_map, water_feature_label_map):
    landmass_label_lookup = produce_label_dict(landmass_label_map)
    continent_label_lookup = {}
    land_feature_label_lookup = {}

    water_body_label_lookup = produce_label_dict(water_body_label_map)
    ocean_label_lookup = {}
    water_feature_label_lookup = {}


    label_lookups = {
        'landmass': landmass_label_lookup,
        'continent': continent_label_lookup,
        'land_feature': land_feature_label_lookup,
        'water_body': water_body_label_lookup,
        'ocean': ocean_label_lookup,
        'water_feature': water_feature_label_lookup
    }
    return label_lookups




