from generation.generator_main import generate_data_maps

class WorldData:
    def __init__(self, rows, cols, biome_config):
        self.rows, self.cols = rows, cols
        self.world_data = generate_data_maps(self.rows, self.cols, biome_config)
        
    def get_cell_data(self, pos):
        r, c = pos

        cell_data = {}
        
        for map in self.world_data:
            cell_data[map] = self.world_data[map][r, c]

        return cell_data

    def get_world_data(self):
        return self.world_data
    
    def get_biome_data(self, x0, y0, x1, y1):
        biome_data = {}

        for map in self.world_data:
            biome_data[map] = self.world_data[map][y0:y1, x0:x1]

        return biome_data
    
    def set_map_data(self, map_name, data):
        self.world_data[map_name][:] = data
    
    def set_map_data_at(self, map_name, pos, data):
        self.world_data[map_name][pos] = data


    