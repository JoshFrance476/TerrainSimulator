from simulation.world_data import WorldData
import numpy as np
import config as config

class World:
    """Handles simulator and high level world logic."""

    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.data = WorldData(rows, cols)

        self.tick_count = 0

        
    def step(self):
        self.tick_count += 1

    def get_world_data(self):
        return self.data.get_world_data()  
    
    def get_map_data(self, map_name):
        return self.data.get_world_data()[map_name]
    
    def set_map_data(self, map_name, data):
        self.data.set_map_data(map_name, data)
    
    def set_map_data_at(self, map_name, pos, data):
        self.data.set_map_data_at(map_name, pos, data)
    
    def get_biome_data(self, x0, y0, x1, y1):
        return self.data.get_biome_data(x0, y0, x1, y1)

    def get_cell_data(self, selected_cell):
        if selected_cell:
            return self.data.get_cell_data(selected_cell), selected_cell,
        else:
            return None, None
    
    def get_surrounding_data_map(self, r, c, radius=3, map="all"):
        r0, r1 = max(0, r-radius), min(self.rows, r+radius+1)
        c0, c1 = max(0, c-radius), min(self.cols, c+radius+1)

        if map == "all":
            return self.data.get_biome_data(c0, r0, c1, r1)
        else:
            return self.data.get_biome_data(c0, r0, c1, r1)[map]
    
    def get_surrounding_data_dict(self, r, c, radius=3, map="biome"):
        data_map = self.get_surrounding_data_map(r, c, radius, map)
        ids, counts = np.unique(data_map, return_counts=True)
        result = {}
        for id, count in zip(ids, counts):
            biome_name = config.BIOME_RULES[id]["name"]
            result[biome_name] = int(count)
        return result









    


