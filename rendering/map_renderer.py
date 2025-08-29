import pygame
from utils import config
from overlays.overlay_generator import generate_territory_overlay, apply_heatmap_overlay

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""

    def __init__(self):
        pass
    

    def generate_static_overlays(self, world_data):
        self.pop_capacity_overlay = apply_heatmap_overlay(
                    world_data["population_capacity"],
                    world_data["elevation"]
                )
    
    def render_view(self, screen, terrain_data, map_filter, camera):
        '''Takes in world data and filter to produce display map, then draws to screen'''
        display_map = self.apply_overlay(terrain_data, map_filter)
        self.draw_map_to_screen(screen, display_map, camera)

    
    def apply_overlay(self, terrain_data, map_filter):
        '''Applies selected overlay to the base colour map.'''

        if map_filter == 1:
            display_map = self.pop_capacity_overlay
        else:
            display_map = terrain_data

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
