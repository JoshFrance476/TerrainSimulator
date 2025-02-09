import pygame
from utils import config
from drawing_logic import draw_terrain, draw_hover_highlight

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""

    def __init__(self):
        self.surface_cache = None  # Caching pre-rendered terrain for optimization
        self.current_step = 0

    def draw_map(self, screen, display_map, step_counter, camera):
        """Draws the terrain map and overlays."""
        screen.fill((0, 0, 0))  # Clear screen
        
        camera.clamp_pan()
        
        # Always ensure we have a low-res surface cache
        if self.surface_cache is None or self.current_step != step_counter:
            self.surface_cache = self.generate_surface(display_map)
            self.current_step = step_counter
        

        # Draw terrain with LOD consideration
        self.draw_terrain_with_zoom(screen, display_map, camera)

    def generate_surface(self, display_map):
        """Generates a Pygame surface from the terrain data."""
        rows, cols = len(display_map), len(display_map[0])
        surface = pygame.Surface((cols * config.CELL_SIZE, rows * config.CELL_SIZE))
        for r in range(rows):
            for c in range(cols):
                pygame.draw.rect(
                    surface, 
                    display_map[r][c], 
                    (c * config.CELL_SIZE, r * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
                )
        return surface

    def draw_terrain_with_zoom(self, screen, display_map, camera):
        """Handles zooming and panning while drawing the terrain with LOD."""
        if camera.zoom_level > config.LOD_THRESHOLD:
            # High-detail mode (render individual cells)
            cell_size = config.CELL_SIZE * camera.zoom_level
            
            # Round offsets for pixel-perfect rendering
            x_offset_int = round(camera.x_offset)
            y_offset_int = round(camera.y_offset)
            
            for r in range(config.ROWS):
                for c in range(config.COLS):
                    colour = display_map[r][c]
                    
                    # Convert grid position to screen position
                    x = round(c * cell_size - x_offset_int)
                    y = round(r * cell_size - y_offset_int)
                    
                    # Only render visible cells
                    if -cell_size < x < config.WIDTH and -cell_size < y < config.HEIGHT:
                        pygame.draw.rect(
                            screen,
                            colour,
                            (x, y, round(cell_size + 0.5), round(cell_size + 0.5))
                        )
        else:
            # Low-detail mode (use cached surface)
            scaled_width = int(self.surface_cache.get_width() * camera.zoom_level)
            scaled_height = int(self.surface_cache.get_height() * camera.zoom_level)
            scaled_surface = pygame.transform.smoothscale(
                self.surface_cache,
                (scaled_width, scaled_height)
            )
            screen.blit(scaled_surface, (-camera.x_offset, -camera.y_offset))

    def draw_hover_effect(self, screen, hovered_cell, camera):
        """Draws a hover effect on the currently selected cell."""
        if hovered_cell:
            draw_hover_highlight(
                screen, 
                hovered_cell, 
                camera.x_offset, 
                camera.y_offset, 
                camera.zoom_level, 
                config.CELL_SIZE, 
                (255, 255, 255, 50)
            )
