import pygame
import config
from utils.colour_utils import hsv_to_rgb_array
from utils.produce_border_maps import produce_region_border_surface, produce_chunk_border_surface

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""
    def __init__(self, world, camera, state):
        self.world = world
        self.camera = camera
        self.state = state

        self.map_surface = None
        self.region_border_surface = None
        self.refresh_view()
    
    def refresh_view(self):
        x0, y0, x1, y1 = self.camera.get_boundaries()
        colour_map = self.world.get_world_data()['colour'][y0:y1,x0:x1].copy()


        self.map_surface = self.produce_map_surface(colour_map)

        if self.state.debug_mode:
            chunk_view = self.world.get_chunk_map()[y0:y1,x0:x1]
            self.region_border_surface = produce_chunk_border_surface(chunk_view)
        else:
            region_view = [row[x0:x1] for row in self.world.get_region_map()[y0:y1]]
            self.region_border_surface = produce_region_border_surface(region_view)
    

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
