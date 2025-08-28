import pygame
from utils import config
from overlays.overlay_generator import generate_territory_overlay, apply_heatmap_overlay

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""

    def __init__(self):
        self.surface_cache = None  # Caching pre-rendered terrain for optimization
        self.current_step = 0

    def render_view(self, screen, world_data, map_filter, camera):
        '''Takes in world data and filter to produce display map, then draws to screen'''
        display_map = self.apply_overlay(world_data, map_filter)
        self.draw_map_to_screen(screen, display_map, camera)

    
    def apply_overlay(self, world_data, map_filter):
        '''Applies selected overlay to the base colour map.'''
        static_maps, dynamic_maps, display_map = world_data

        if map_filter == 1:
            display_map = apply_heatmap_overlay(
                    dynamic_maps["population_map"],
                    static_maps["elevation_map"]
                )
        return display_map


    
    def draw_map_to_screen(self, screen, display_map, camera):
        '''Draws the given display map to the screen based on camera position.'''
        screen.fill((0, 0, 0))

        for r in range(config.CAMERA_ROWS):
            for c in range(config.CAMERA_COLS):
                colour = display_map[r+camera.y_pos][c+camera.x_pos]
                pygame.draw.rect(
                    screen,
                    colour,
                    (c * config.CELL_SIZE, r * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
                )
