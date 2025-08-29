from utils.colour_utils import generate_color_map
from generation.generator_main import generate_static_maps, generate_dynamic_maps, update_dynamic_maps




class World:
    """Handles world data generation and updates."""
    def __init__(self):
        self.static_maps_dict = generate_static_maps()
        self.dynamic_maps = generate_dynamic_maps(self.static_maps_dict['desiribility'])

        #Generates initial colour map
        self.terrain_map = generate_color_map(self.static_maps_dict['elevation'], self.static_maps_dict['region'], self.static_maps_dict['steepness'], True, True)


    def update(self):
        self.dynamic_maps = update_dynamic_maps(self.static_maps_dict['desiribility'], self.dynamic_maps['population_map'])


    def get_world_data(self):
        return self.static_maps_dict
    
    def get_terrain_data(self):
        return self.terrain_map
    
    def get_static_data(self):
        return self.static_float_maps, self.static_int_maps
    

    def get_terrain_map(self):
        return self.terrain_map
    
    def get_static_maps(self):
        return self.static_maps

    def get_dynamic_maps(self):
        return self.dynamic_maps



    


