from generation.generator_main import generate_static_maps, generate_dynamic_maps#, update_dynamic_maps
from utils.colour_utils import generate_color_map
import numpy as np
import utils.config as config

class WorldData:
    def __init__(self):
        self.static_float_maps_index, self.static_float_maps, self.static_int_maps_index, self.static_int_maps = self.init_static_maps()

        self.world_data = {}

        # Add static float layers
        for name, idx in self.static_float_maps_index.items():
            self.world_data[name] = self.static_float_maps[idx]

        # Add int layers
        for name, idx in self.static_int_maps_index.items():
            self.world_data[name] = self.static_int_maps[idx]

        self.dynamic_float_maps_index, self.dynamic_float_maps = self.init_dynamic_maps(self.world_data)

        # Add dynamic float layers
        for name, idx in self.dynamic_float_maps_index.items():
            self.world_data[name] = self.dynamic_float_maps[idx]

        self.terrain_map = generate_color_map(self.world_data, True, True)


    def get_world_data(self):
        return self.world_data
    
    def get_terrain_data(self):
        return self.terrain_map
    
    def get_region_data(self, x0, y0, x1, y1):
        return self.static_float_maps[y0:y1, x0:x1], self.static_int_maps[y0:y1, x0:x1], self.dynamic_float_maps[y0:y1, x0:x1], self.terrain_map[y0:y1, x0:x1]

    



    def init_static_maps(self):
        elevation_map, rainfall_map, temperature_map, river_map, sea_map, steepness_map, river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map = generate_static_maps()
        
        static_float_layers_index = {
            'elevation': 0,
            'traversal_cost': 1,
            'steepness': 2,
            'fertility': 3,
            'temperature': 4,
            'rainfall': 5,
        }

        static_float_layers = np.zeros((len(static_float_layers_index), config.WORLD_ROWS, config.WORLD_COLS), dtype=np.float32)

        static_float_layers[static_float_layers_index['elevation']] = elevation_map
        static_float_layers[static_float_layers_index['traversal_cost']] = traversal_cost_map
        static_float_layers[static_float_layers_index['steepness']] = steepness_map
        static_float_layers[static_float_layers_index['fertility']] = fertility_map
        static_float_layers[static_float_layers_index['temperature']] = temperature_map
        static_float_layers[static_float_layers_index['rainfall']] = rainfall_map

        static_int_layers_index = {
            'region': 0,
            'river': 1,
            'sea': 2,
            'river_proximity': 3,
            'sea_proximity': 4,
        }

        static_int_layers = np.zeros((len(static_int_layers_index), config.WORLD_ROWS, config.WORLD_COLS), dtype=np.uint8)

        static_int_layers[static_int_layers_index['river']] = river_map.astype(np.uint8)
        static_int_layers[static_int_layers_index['sea']] = sea_map.astype(np.uint8)
        static_int_layers[static_int_layers_index['river_proximity']] = river_proximity_map.astype(np.uint8)
        static_int_layers[static_int_layers_index['sea_proximity']] = sea_proximity_map.astype(np.uint8)

        # Create a lookup table for region names to region ID
        region_lookup = {region: idx for idx, region in enumerate(config.REGION_COLORS.keys())}

        #This code increased peak memory usage significantly, below method is much more effective
        #static_int_layers[static_int_layers_index['region']] = np.vectorize(region_lookup.get)(region_map).astype(np.uint8)

        region_map_int = np.zeros_like(region_map, dtype=np.uint8)
        for region_name, idx in region_lookup.items():
            region_map_int[region_map == region_name] = idx
        static_int_layers[static_int_layers_index['region']] = region_map_int

        return static_float_layers_index, static_float_layers, static_int_layers_index, static_int_layers





    def init_dynamic_maps(self, static_data):
        population_capacity_map, population_map = generate_dynamic_maps(static_data)

        dynamic_float_layers_index = {
            'population_capacity': 0,
            'population': 1,
        }

        dynamic_float_layers = np.zeros((len(dynamic_float_layers_index), config.WORLD_ROWS, config.WORLD_COLS), dtype=np.float32)

        dynamic_float_layers[dynamic_float_layers_index['population']] = population_map
        dynamic_float_layers[dynamic_float_layers_index['population_capacity']] = population_capacity_map

        return dynamic_float_layers_index, dynamic_float_layers