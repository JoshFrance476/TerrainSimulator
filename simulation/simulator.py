from overlays.overlay_generator import generate_territory_overlay, apply_heatmap_overlay
from utils.colour_utils import generate_color_map
from generation.generator_main import generate_static_maps, generate_dynamic_maps, update_dynamic_maps




class Simulator:
    def __init__(self):
        self.static_maps = generate_static_maps()
        self.dynamic_maps = generate_dynamic_maps(self.static_maps)

        #Generates initial colour map
        self.colour_map = generate_color_map(self.static_maps, True, True)
        self.display_map = self.colour_map


    def update(self):
        self.dynamic_maps = update_dynamic_maps(self.static_maps, self.dynamic_maps)


    def get_world_data(self):
        return self.static_maps, self.dynamic_maps, self.display_map

    def get_display_map(self):
        return self.display_map
    
    def get_static_maps(self):
        return self.static_maps

    def get_dynamic_maps(self):
        return self.dynamic_maps



    


