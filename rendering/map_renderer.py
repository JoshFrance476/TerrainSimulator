import pygame
import config
from utils.colour_utils import hsv_to_rgb_array

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""
    def __init__(self, controller):
        self.controller = controller
        self.display_map = self.controller.get_world_data()['colour']
    
    def render_view(self, screen):
        x0, y0, x1, y1 = self.controller.get_camera_boundaries()
        display_map = self.display_map[y0:y1,x0:x1]
        self.draw_view(screen, display_map)


    def draw_view(self, screen, display_map):
        """AI code using surfarray to draw the whole map at once."""
        rgb_map = hsv_to_rgb_array(display_map)

        surface = pygame.surfarray.make_surface(rgb_map.swapaxes(0, 1))
        surface = pygame.transform.scale(surface, (rgb_map.shape[1] * config.CELL_SIZE, 
                                                rgb_map.shape[0] * config.CELL_SIZE))
        screen.blit(surface, (config.SIDEBAR_WIDTH, 0))
