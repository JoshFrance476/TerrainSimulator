from simulation.world_data import WorldData
from simulation.region_manager import RegionManager
from simulation.world_interpreter import WorldInterpreter
import numpy as np
import config as config
import json

class World:
    def __init__(self, rows, cols, biome_config):
        self.rows, self.cols = rows, cols
        self.data = WorldData(rows, cols, biome_config)

        self.biome_config = biome_config

        self.region_manager = RegionManager()

        self.world_interpreter = WorldInterpreter(self.get_map_data("colour").copy(), self.get_map_data("biome").copy())

        self.tick_count = 0

    def get_region_map(self): 
        return self.region_manager.get_region_map()

    def get_chunk_map(self):
        return self.world_interpreter.get_chunk_map()
        
    def step(self):
        self.tick_count += 1
    
    def get_semantic_tile_data(self, location):
        info = {
            "Biome": self.get_biome_at(location),
            "Details": {}
        }
        for region in self.region_manager.get_regions_at_location(location):
            info["Details"][region.title] = {
                "Visible Description": region.visible_desc,
                "Hidden Description": region.hidden_desc
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
    
    def update_biome(self, mask=None):
        self.data.update_biome(mask)
    
    def update_stage_3(self):
        self.data.update_stage_3()
    
    def set_biome_with_mask(self, mask, biome_id):
        self.data.set_biome_with_mask(mask, biome_id)

    def add_region_with_mask(self, mask, region_id):
        self.region_manager.add_region_with_mask(mask, region_id)

    def remove_region_with_mask(self, mask, region_id):
        self.region_manager.remove_region_with_mask(mask, region_id)
    
    def create_region(self):
        return self.region_manager.create_region()

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

    def save_map(self, file_name, starting_location):
        self.biome_config.set_starting_location(starting_location)
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
        
        self.region_manager.region_map = loaded["region_map"]
        self.region_manager.region_list = loaded["region_list"].tolist()

        self.region_manager.rid_counter = 0
        
        self.biome_config.load_biome_config_file(json.loads(str(loaded['biome_config'])))

        self.world_interpreter = WorldInterpreter(self.get_map_data("colour").copy(), self.get_map_data("biome").copy())







    


