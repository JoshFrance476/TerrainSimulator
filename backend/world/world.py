from world.world_data import WorldData
from world.regions.region_manager import RegionManager
from world.chunks.chunk_manager import ChunkManager
from generation.biome_config_manager import BiomeConfigManager
import config as config
from utils.grid_utils import find_path_dijkstra, find_path_astar

class World:
    """
    Organisation:
    Loading/Saving
    World Data
    Biome Config
    Chunks
    Regions
    """
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.data = None
        self.region_manager = None
        self.chunk_manager = None
        self.biome_config = None

        self.current_path = None


    # Loading/Saving ############################################################################################
    def load_world(self, biome_config, world_data, region_list):
        self.biome_config = BiomeConfigManager(biome_config)

        self.data = WorldData(self.rows, self.cols, self.biome_config, world_data)

        self.region_manager = RegionManager(self.rows, self.cols, world_data["region_map"], region_list)

        self.chunk_manager = ChunkManager(self.rows, self.cols, self.get_map_data("colour").copy(), self.get_map_data("biome").copy(), self.biome_config)
    
    def get_all_map_data(self):
        map_data = self.data.get_world_data()
        map_data["region_map"] = self.region_manager.region_map
        return map_data

    def get_biome_config(self):
        biome_config = {
                "constants": self.biome_config.constants,
                "biomes": self.biome_config.biomes
        }
        return biome_config

    def get_region_list(self):
        return [r.to_dict() for r in self.region_manager.region_list]
    
    def get_data(self):
        biome_config = {
                "constants": self.biome_config.constants,
                "biomes": self.biome_config.biomes
        }
        
        map_data = self.data.world_data

        region_list = self.region_manager.region_list

        map_data["region_map"] = self.region_manager.region_map

        return map_data, region_list, biome_config


    # World Data ############################################################################################


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
            return self.data.get_cell_data(selected_cell)
        else:
            return None
    
    def get_tile_data_json(self, location):
        biome_data = self.get_biome_data_at_location(location)
        info = {
            "Biome": biome_data["name"],
            "Biome Description": biome_data["description"],
            "Details": {}
        }
        for region in self.region_manager.get_regions_at_location(location):
            info["Details"][region.title] = {
                "Visible Description": region.visible_desc,
                "Hidden Description": region.hidden_desc
            }
        return info


    # Biome Config ############################################################################################

    def get_biome_lookup(self):
        return self.biome_config.get_biome_lookup()

    def get_biome_data_at_location(self, location):
        return self.biome_config.biomes[(self.get_cell_data(location)['biome'])]
    
    def get_biome_data_from_id(self, biome_id):
        return self.biome_config.biomes[biome_id]


    def get_biomes(self):
        return self.biome_config.biomes

    def get_starting_location(self):
        return self.biome_config.get_starting_location()

    def add_biome(self, name, h, s, v, trav_cost, description):
        self.biome_config.add_biome(name, h, s, v, trav_cost, description)
    
    def edit_biome(self, biome_index, new_name, new_h, new_s, new_v, new_trav_cost, description):
        self.biome_config.edit_biome(biome_index, new_name, new_h, new_s, new_v, new_trav_cost, description)

    def get_biome_map(self):
        return self.get_map_data("biome")
    
    # Chunks ############################################################################################


    def get_chunk_map(self):
        return self.chunk_manager.get_chunk_map()

    def get_chunk_id_at(self, location):
        return self.chunk_manager.get_id_at(location)
    
    def get_closest_chunks(self, location, count=5):
        return self.chunk_manager.get_closest_chunks(location, count)

    def get_chunk_context_json(self, location):
        return self.chunk_manager.get_surroundings_json(location)


    # Regions ##############################################################################################

    def get_region_lookup(self):
        return self.region_manager.get_region_lookup()
    
    def get_region_map(self): 
        return self.region_manager.get_region_map()
    
    def get_regions_at_location(self, location):
        return self.region_manager.get_regions_at_location(location)

    def get_region(self, region_id):
        return self.region_manager.get_region(region_id)
    
    def add_region_with_mask(self, mask, region_id):
        self.region_manager.add_region_with_mask(mask, region_id)

    def remove_region_with_mask(self, mask, region_id):
        self.region_manager.remove_region_with_mask(mask, region_id)
    
    def create_region(self):
        return self.region_manager.create_region()

    def add_new_region_to_chunk(self, chunk_id, title, visible_desc, hidden_desc):
        location = self.chunk_manager.get_random_location_in_chunk(chunk_id)
        self.region_manager.create_region_at_location(location, title, visible_desc, hidden_desc)
    

    # Pathfinding ############################################################################################


    def find_path(self, start, end):
        traversal_map = self.get_map_data("traversal_cost")
        path = find_path_dijkstra(start, end, traversal_map)
        return path

    def set_path(self, path):
        self.current_path = path
    
    def clear_path(self):
        self.current_path = None