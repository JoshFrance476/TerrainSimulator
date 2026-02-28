from simulation.world_data import WorldData
from simulation.region_manager import RegionManager
import numpy as np
import config as config
import json

class World:
    """Handles simulator and high level world logic."""

    def __init__(self, rows, cols, biome_config):
        self.rows, self.cols = rows, cols
        self.data = WorldData(rows, cols, biome_config)

        self.biome_config = biome_config

        self.region_manager = RegionManager()

        self.tick_count = 0

    def get_region_map(self): 
        return self.region_manager.get_region_map()
        
    def step(self):
        self.tick_count += 1
    
    def get_semantic_tile_data(self, location):
        region_list = []
        for region in self.region_manager.get_regions_at_location(location):
            region_list.append(region.title + ": "+region.visible_desc+", "+region.hidden_desc)
        info = {
            "Tile": self.get_biome_at(location),
            "Details": ". ".join(region_list)
        }
        return info

    def get_regions_at_location(self, location):
        return self.region_manager.get_regions_at_location(location)

    def get_region(self, region_id):
        return self.region_manager.get_region(region_id)
    
    def apply_edit_elevation_mask(self, mask):
        self.data.world_data['elevation'] += mask
    
    def apply_smoothing_elevation_mask(self, mask):
        elevation = self.data.world_data['elevation']
        selected = elevation[mask]

        average = selected.mean()

        elevation[mask] = elevation[mask] + 0.1 * (average - elevation[mask])

    def update_steepness(self):
        self.data.update_steepness()
    
    def update_biome(self):
        self.data.update_biome()
    
    def update_stage_3(self):
        self.data.update_stage_3()

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

    def get_biome_at(self, location):
        return self.data.get_biome_at(location)

    def get_cell_data(self, selected_cell):
        if selected_cell:
            return self.data.get_cell_data(selected_cell)
        else:
            return None
    
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

    def save_map(self, file_name):
        np.savez(
            file_name,
            # numeric maps
            **self.data.world_data,

            # region manager (python objects)
            region_map=np.array(self.region_manager.region_map, dtype=object),
            region_list=np.array(self.region_manager.region_list, dtype=object),

            biome_config = json.dumps({
                "constants": self.biome_config.constants,
                "biomes": self.biome_config.biomes
})
        )

    
    def load_map(self, file_name):
        loaded = np.load(file_name, allow_pickle=True)

        # restore numeric maps only
        self.data.world_data = {
            k: loaded[k]
            for k in loaded.files
            if k not in ("region_map", "region_list", "biome_config")
        }

        # restore region manager
        self.region_manager.region_map = loaded["region_map"].tolist()
        self.region_manager.region_list = loaded["region_list"].tolist()
        
        self.biome_config.load_biome_config_file(json.loads(str(loaded['biome_config'])))









    


