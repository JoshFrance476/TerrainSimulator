from utils.colour_utils import generate_color_map
from generation.generator_main import generate_static_maps, generate_dynamic_maps, update_dynamic_maps




class World:
    """Handles world data generation and updates."""
    def __init__(self):
        self.static_maps_dict = generate_static_maps()
        self.dynamic_maps_dict = generate_dynamic_maps(self.static_maps_dict)

        #Generates initial colour map
        self.terrain_map = generate_color_map(self.static_maps_dict, True, True)


    def update(self):
        self.dynamic_maps = update_dynamic_maps(self.static_maps_dict, self.dynamic_maps_dict)


    def get_world_data(self):
        return self.static_maps_dict, self.dynamic_maps_dict
    
    def get_terrain_data(self):
        return self.terrain_map


    def get_terrain_map(self):
        return self.terrain_map
    
    def get_static_maps(self):
        return self.static_maps

    def get_dynamic_maps(self):
        return self.dynamic_maps



    


