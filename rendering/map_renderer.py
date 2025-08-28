import pygame
from utils import config

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""

    def __init__(self):
        self.surface_cache = None  # Caching pre-rendered terrain for optimization
        self.current_step = 0

    def draw_map(self, screen, display_map, camera):
        """Draws the terrain map and overlays."""
        screen.fill((0, 0, 0))  # Clear screen
        
        camera.clamp_pan()     

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
