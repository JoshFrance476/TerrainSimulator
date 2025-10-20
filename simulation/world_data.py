from generation.generator_main import generate_data_maps
import numpy as np
import config as config
import utils.map_utils


class WorldData:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.world_data = generate_data_maps(self.rows, self.cols)



    def update(self):
        pass
        #self.world_data["population"] *= np.random.uniform(0.97, 1.05)

    
    def get_cell_data(self, pos):
        r, c = pos

        cell_data = {}
        
        for map in self.world_data:
            cell_data[map] = self.world_data[map][r, c]

        return cell_data



    def get_world_data(self):
        return self.world_data
    
    
    def get_region_data(self, x0, y0, x1, y1):
        region_data = {}

        for map in self.world_data:
            region_data[map] = self.world_data[map][y0:y1, x0:x1]

        return region_data
    
    def set_map_data(self, map_name, data):
        self.world_data[map_name][:] = data
    
    def set_map_data_at(self, map_name, pos, data):
        self.world_data[map_name][pos] = data


    def find_x_largest_values(self, map_name, x):
        return utils.map_utils.find_x_largest_value_locations(self.world_data[map_name], x)

    