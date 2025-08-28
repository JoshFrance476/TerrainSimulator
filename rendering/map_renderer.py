import pygame
from utils import config
from overlays.overlay_generator import generate_territory_overlay, apply_heatmap_overlay

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""

    def __init__(self):
        self.surface_cache = None  # Caching pre-rendered terrain for optimization
        self.current_step = 0

    def draw_map(self, screen, world_data, map_filter, camera):
        static_maps, dynamic_maps, display_map = world_data
        """Draws the terrain map and overlays."""
        screen.fill((0, 0, 0))  # Clear screen
        
        camera.clamp_pan()     

        if map_filter == 1:
            display_map = apply_heatmap_overlay(
                    dynamic_maps["population_map"],
                    static_maps["elevation_map"]
                )


        self.draw_terrain(screen, display_map, camera)


    
    def draw_terrain(self, screen, display_map, camera):
        for r in range(config.CAMERA_ROWS):
            for c in range(config.CAMERA_COLS):
                colour = display_map[r+camera.y_pos][c+camera.x_pos]
                pygame.draw.rect(
                    screen,
                    colour,
                    (c * config.CELL_SIZE, r * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
                )
