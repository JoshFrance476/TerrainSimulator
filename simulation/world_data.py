from generation.generator_main import generate_maps
from utils.colour_utils import generate_color_map
import numpy as np
import utils.config as config
import utils.map_utils


class WorldData:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.float_layers_index, self.float_layers, self.int_layers_index, self.int_layers, self.colour_map = self.init_maps()
        self.world_data = {'colour': self.colour_map}

        # Add static float layers
        for name, idx in self.float_layers_index.items():
            self.world_data[name] = self.float_layers[idx]

        # Add int layers
        for name, idx in self.int_layers_index.items():
            self.world_data[name] = self.int_layers[idx]


    #def update(self):
        #pass
        #self.world_data["population"] = update_population_granular(self.world_data)

    
    def get_cell_data(self, pos):
        r, c = pos

        cell_data = {}
        for name, idx in self.float_layers_index.items():
            cell_data[name] = float(self.float_layers[idx][r, c])

        for name, idx in self.int_layers_index.items():
            cell_data[name] = int(self.int_layers[idx][r, c])

        cell_data['colour'] = tuple(self.colour_map[r, c])

        return cell_data



    def get_world_data(self):
        return self.world_data
    
    def get_terrain_data(self):
        return self.colour_map
    
    def get_region_data(self, x0, y0, x1, y1):
        region_data = {}

        for name, idx in self.float_layers_index.items():
            region_data[name] = self.float_layers[idx][y0:y1, x0:x1]

        for name, idx in self.int_layers_index.items():
            region_data[name] = self.int_layers[idx][y0:y1, x0:x1]
        
        region_data['colour'] = self.colour_map[y0:y1, x0:x1]



        return region_data
    
    def set_map_data(self, map_name, data):
        self.world_data[map_name][:] = data
    
    def set_map_data_at(self, map_name, pos, data):
        self.world_data[map_name][pos] = data


    def find_x_largest_values(self, map_name, x):
        return utils.map_utils.find_x_largest_value_locations(self.world_data[map_name], x)

    


    

    def init_maps(self):
        elevation_map, rainfall_map, temperature_map, river_map, sea_map, steepness_map, coastline_map, river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map, population_capacity_map, population_map, resource_map = generate_maps(self.rows, self.cols)
        
        float_layers_index = {
            'elevation': 0,
            'traversal_cost': 1,
            'steepness': 2,
            'fertility': 3,
            'temperature': 4,
            'rainfall': 5,
            'population_capacity': 6,
            'population': 7,
            'flip_probability': 8,
            'decay_probability': 9
        }

        float_layers = np.zeros((len(float_layers_index), self.rows, self.cols), dtype=np.float32)

        float_layers[float_layers_index['elevation']] = elevation_map
        float_layers[float_layers_index['traversal_cost']] = traversal_cost_map
        float_layers[float_layers_index['steepness']] = steepness_map
        float_layers[float_layers_index['fertility']] = fertility_map
        float_layers[float_layers_index['temperature']] = temperature_map
        float_layers[float_layers_index['rainfall']] = rainfall_map
        float_layers[float_layers_index['population_capacity']] = population_capacity_map
        float_layers[float_layers_index['population']] = population_map
        float_layers[float_layers_index['flip_probability']] = np.zeros((self.rows, self.cols), dtype=np.float32)
        float_layers[float_layers_index['decay_probability']] = np.zeros((self.rows, self.cols), dtype=np.float32)
        
        int_layers_index = {
            'region': 0,
            'river': 1,
            'sea': 2,
            'river_proximity': 3,
            'sea_proximity': 4,
            'coastline': 5,
            'resource': 6,
            'state': 7,
            'settlement_distance': 8,
            'neighbor_counts': 9
        }

        int_layers = np.zeros((len(int_layers_index), self.rows, self.cols), dtype=np.uint8)

        int_layers[int_layers_index['river']] = river_map.astype(np.uint8)
        int_layers[int_layers_index['sea']] = sea_map.astype(np.uint8)
        int_layers[int_layers_index['river_proximity']] = river_proximity_map.astype(np.uint8)
        int_layers[int_layers_index['sea_proximity']] = sea_proximity_map.astype(np.uint8)
        int_layers[int_layers_index['coastline']] = coastline_map.astype(np.uint8)
        int_layers[int_layers_index['resource']] = resource_map.astype(np.uint8)
        int_layers[int_layers_index['state']] = np.full((self.rows, self.cols), 255, dtype=np.int32)
        int_layers[int_layers_index['settlement_distance']] = np.full((self.rows, self.cols), 0, dtype=np.int32)
        int_layers[int_layers_index['neighbor_counts']] = np.full((self.rows, self.cols), 0, dtype=np.int32)

        for region_name, idx in config.REGION_LOOKUP.items():
            region_map[region_map == region_name] = idx
        int_layers[int_layers_index['region']] = region_map

        colour_map = generate_color_map({
            'elevation': elevation_map,
            'region': region_map,
            'steepness': steepness_map
        }, True, True)

        return float_layers_index, float_layers, int_layers_index, int_layers, colour_map
