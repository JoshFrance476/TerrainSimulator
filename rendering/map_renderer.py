import pygame
import config
from utils.colour_utils import hsv_to_rgb_array

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""
    def __init__(self, controller):
        self.controller = controller
        self.colour_map = self.controller.get_world_data()['colour']
        self.region_map = self.controller.world.get_region_map()

        self.display_map = None
        self.refresh_view()
    
    def refresh_view(self):
        x0, y0, x1, y1 = self.controller.get_camera_boundaries()
        colour_map = self.colour_map[y0:y1,x0:x1]
        region_map = [row[x0:x1] for row in self.controller.world.get_region_map()[y0:y1]]

        display_map = colour_map.copy()

        for y, row in enumerate(region_map):
            for x, cell in enumerate(row):
                if cell:
                    display_map[y][x] = 0

        self.display_map = display_map



    def render_view(self, screen):
        """AI code using surfarray to draw the whole map at once."""
        rgb_map = hsv_to_rgb_array(self.display_map)

        surface = pygame.surfarray.make_surface(rgb_map.swapaxes(0, 1))
        surface = pygame.transform.scale(surface, (rgb_map.shape[1] * config.CELL_SIZE, 
                                                rgb_map.shape[0] * config.CELL_SIZE))
        screen.blit(surface, (config.SIDEBAR_WIDTH, 0))
