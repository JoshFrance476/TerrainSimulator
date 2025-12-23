from utils.colour_utils import generate_color_map
from utils.map_utils import produce_landmass_label_map, produce_continent_label_map, produce_ocean_label_map, produce_water_body_label_map

import numpy as np
import time
import logging
import config as config

from utils.map_utils import generate_perlin_noise_map
from generation.stage_1_generator import calculate_temperature
from generation.stage_2_generator import calculate_steepness, generate_coastline_map, generate_sea_map, generate_rivers_map
from generation.stage_3_generator import calculate_proximity_map, determine_region, calculate_soil_fertility, calculate_traversal_cost
from generation.stage_4_generator import calculate_population_capacity_map, init_population, calculate_resource_map

logging.basicConfig(level=logging.DEBUG)



def generate_data_maps(rows, cols):

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
    sea_map = generate_sea_map(elevation_map)
    logging.debug(f"Sea map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_map = generate_rivers_map(elevation_map, config.SEA_LEVEL, config.RIVER_SOURCE_MIN_ELEVATION, config.NUMBER_OF_RIVERS)
    logging.debug(f"River map generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    steepness_map = calculate_steepness(elevation_map)
    logging.debug(f"Steepness map generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    coastline_map = generate_coastline_map(elevation_map)
    logging.debug(f"Coastline map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_proximity_map = calculate_proximity_map(river_map)
    logging.debug(f"River proximity map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    sea_proximity_map = calculate_proximity_map(sea_map)
    logging.debug(f"Sea proximity map generation took {time.time() - start_time:.2f} seconds")

    ## Stage 3

    start_time = time.time()
    region_map = determine_region(elevation_map, temperature_map, rainfall_map, sea_proximity_map, river_proximity_map)
    logging.debug(f"Region map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    fertility_map = calculate_soil_fertility(region_map, rainfall_map, elevation_map, temperature_map)
    logging.debug(f"Fertility map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    traversal_cost_map = calculate_traversal_cost(region_map, steepness_map)  
    logging.debug(f"Traversal cost map generation took {time.time() - start_time:.2f} seconds")

    # Stage 4

    start_time = time.time()
    population_capacity_map = calculate_population_capacity_map(fertility_map, temperature_map, river_proximity_map, sea_map, river_map)
    logging.debug(f"Population capacity map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    population_map = init_population(population_capacity_map)
    logging.debug(f"Population map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    resource_map = calculate_resource_map(fertility_map, temperature_map, elevation_map, region_map, rainfall_map)   
    logging.debug(f"Resource map generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    colour_map = generate_color_map({
        'elevation': elevation_map,
        'region': region_map,
        'steepness': steepness_map
    }, True, True)
    logging.debug(f"Colour map generation took {time.time() - start_time:.2f} seconds")

    land_map = ~sea_map

    start_time = time.time()
    water_body_label_map, water_body_dict = produce_water_body_label_map(sea_map)  #water body map labels every separate water body

    ocean_label_map, ocean_dict = produce_ocean_label_map(water_body_label_map, threshold=200)  #ocean map labels all water bodies larger than threshold
    landmass_label_map, landmass_dict = produce_landmass_label_map(land_map, ocean_label_map)  #landmass map labels every separate landmass, including lakes (water bodies below ocean threshold)

    #continent map labels each section of landmass that is separated by less than (threshold * 2) - 1 cells to the rest of the landmass (ignoring lakes)
    continent_label_map, continent_dict = produce_continent_label_map(landmass_label_map, threshold=4)  

    land_feature_label_map = np.zeros_like(sea_map)

    land_feature_dict = {}
    water_feature_dict = {}

    water_feature_label_map = np.zeros_like(sea_map)

    logging.debug(f"Label map generation took {time.time() - start_time:.2f} seconds")

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
        'land_feature_label': land_feature_label_map,
        'water_body_label': water_body_label_map,
        'ocean_label': ocean_label_map,
        'water_feature_label': water_feature_label_map
        }
    
    label_lookups = {
        'landmass': landmass_dict,
        'continent': continent_dict,
        'land_feature': land_feature_dict,
        'water_body': water_body_dict,
        'ocean': ocean_dict,
        'water_feature': water_feature_dict
    }

    
    return world_data, label_lookups






