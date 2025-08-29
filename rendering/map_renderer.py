import pygame
from utils import config
from overlays.overlay_generator import generate_territory_overlay, apply_heatmap_overlay

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""

    def __init__(self):
        pass
    
    
    def render_view(self, screen, view_data, map_filter):
        '''Takes in world data and filter to produce display map, then draws to screen'''
        display_map = self.apply_overlay(view_data, map_filter)
        self.draw_map_to_screen(screen, display_map)

    
    def apply_overlay(self, view_data, map_filter):
        '''Applies selected overlay to the base colour map.'''

        if map_filter == 1:
            display_map = apply_heatmap_overlay(
                    view_data["population_capacity"],
                    view_data["elevation"]
                )
        else:
            display_map = view_data['terrain']

        return display_map


    
    def draw_map_to_screen(self, screen, display_map):
        """AI code using surfarray to draw the whole map at once."""
        surface = pygame.surfarray.make_surface(display_map.swapaxes(0, 1))  
        surface = pygame.transform.scale(surface, (display_map.shape[1] * config.CELL_SIZE,
                                                display_map.shape[0] * config.CELL_SIZE))
        screen.blit(surface, (0, 0))
