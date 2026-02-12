import pygame
import config
from utils.colour_utils import hsv_to_rgb_array
from utils.region_border_map import produce_region_border_surface

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""
    def __init__(self, controller):
        self.controller = controller
        self.colour_map = self.controller.get_world_data()['colour']
        self.region_map = self.controller.world.get_region_map()

        self.map_surface = None
        self.region_border_surface = None
        self.refresh_view()
    
    def refresh_view(self):
        x0, y0, x1, y1 = self.controller.get_camera_boundaries()
        colour_map = self.colour_map[y0:y1,x0:x1].copy()
        region_map = [row[x0:x1] for row in self.controller.world.get_region_map().copy()[y0:y1]]


        self.map_surface = self.produce_map_surface(colour_map)
        self.region_border_surface = produce_region_border_surface(region_map)
    

    def produce_map_surface(self, colour_map):
        rgb_map = hsv_to_rgb_array(colour_map)

        map_surface = pygame.surfarray.make_surface(rgb_map.swapaxes(0, 1))
        map_surface = pygame.transform.scale(map_surface, (rgb_map.shape[1] * config.CELL_SIZE, 
                                                rgb_map.shape[0] * config.CELL_SIZE))
        return map_surface
        


    def render_view(self, screen):
        """AI code using surfarray to draw the whole map at once."""
    
        screen.blit(self.map_surface, (config.SIDEBAR_WIDTH, 0))
        screen.blit(self.region_border_surface, (config.SIDEBAR_WIDTH, 0))
