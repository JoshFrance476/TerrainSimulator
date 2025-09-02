from generation.generator_main import generate_static_maps, generate_dynamic_maps#, update_dynamic_maps
from utils.colour_utils import generate_color_map
import numpy as np
import utils.config as config


class WorldData:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.static_float_maps_index, self.static_float_maps, self.static_int_maps_index, self.static_int_maps, self.colour_map = self.init_static_maps()
        self.world_data = {'colour': self.colour_map}

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

    def update(self):
        pass
        #self.world_data["population"] = update_population_granular(self.world_data)




    def get_world_data(self):
        return self.world_data
    
    def get_terrain_data(self):
        return self.colour_map
    
    def get_region_data(self, x0, y0, x1, y1):
        region_data = {}

        for name, idx in self.static_float_maps_index.items():
            region_data[name] = self.static_float_maps[idx][y0:y1, x0:x1]

        for name, idx in self.static_int_maps_index.items():
            region_data[name] = self.static_int_maps[idx][y0:y1, x0:x1]

        for name, idx in self.dynamic_float_maps_index.items():
            region_data[name] = self.dynamic_float_maps[idx][y0:y1, x0:x1]
        
        region_data['colour'] = self.colour_map[y0:y1, x0:x1]

        return region_data
    

    


    

    def init_static_maps(self):
        elevation_map, rainfall_map, temperature_map, river_map, sea_map, steepness_map, coastline_map, river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map = generate_static_maps(self.rows, self.cols)
        
        static_float_layers_index = {
            'elevation': 0,
            'traversal_cost': 1,
            'steepness': 2,
            'fertility': 3,
            'temperature': 4,
            'rainfall': 5,
        }

        static_float_layers = np.zeros((len(static_float_layers_index), self.rows, self.cols), dtype=np.float32)

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
            'coastline': 5,
        }

        static_int_layers = np.zeros((len(static_int_layers_index), self.rows, self.cols), dtype=np.uint8)

        static_int_layers[static_int_layers_index['river']] = river_map.astype(np.uint8)
        static_int_layers[static_int_layers_index['sea']] = sea_map.astype(np.uint8)
        static_int_layers[static_int_layers_index['river_proximity']] = river_proximity_map.astype(np.uint8)
        static_int_layers[static_int_layers_index['sea_proximity']] = sea_proximity_map.astype(np.uint8)
        static_int_layers[static_int_layers_index['coastline']] = coastline_map.astype(np.uint8)



        for region_name, idx in config.REGION_LOOKUP.items():
            region_map[region_map == region_name] = idx
        static_int_layers[static_int_layers_index['region']] = region_map

        colour_map = generate_color_map({
            'elevation': elevation_map,
            'region': region_map,
            'steepness': steepness_map
        }, True, True)

        return static_float_layers_index, static_float_layers, static_int_layers_index, static_int_layers, colour_map





    def init_dynamic_maps(self, static_data):
        population_capacity_map, population_map = generate_dynamic_maps(static_data)

        dynamic_float_layers_index = {
            'population_capacity': 0,
            'population': 1,
        }

        dynamic_float_layers = np.zeros((len(dynamic_float_layers_index), self.rows, self.cols), dtype=np.float32)

        dynamic_float_layers[dynamic_float_layers_index['population']] = population_map
        dynamic_float_layers[dynamic_float_layers_index['population_capacity']] = population_capacity_map

        return dynamic_float_layers_index, dynamic_float_layers