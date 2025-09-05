import pygame
from utils import config
from overlays.overlay_generator import apply_heatmap_overlay

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""

    def __init__(self):
        self.selected_filter_name = "None"
    
    def render_view(self, screen, view_data, map_filter):
        '''Takes in world data and filter to produce display map, then draws to screen'''
        display_map = self.apply_overlay(view_data, map_filter)
        self.draw_view(screen, display_map)
        
    
    def render_magnifier(self, screen, magnifier_map, map_filter, hovered_cell, camera_x_pos, camera_y_pos):
        magnifier_display_map = self.apply_overlay(magnifier_map, map_filter)
        self.draw_magnifier(screen, magnifier_display_map, hovered_cell, camera_x_pos, camera_y_pos)

    
    def apply_overlay(self, view_data, map_filter):
        '''Applies selected overlay to the base colour map.'''
        if map_filter == 0:
            display_map = view_data["colour"]
            self.selected_filter_name = "None"
        elif map_filter == 1:
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["elevation"]
                )
            self.selected_filter_name = "Elevation"
        elif map_filter == 2:
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["temperature"]
                )
            self.selected_filter_name = "Temperature"
        elif map_filter == 3:
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["rainfall"]
                )
            self.selected_filter_name = "Rainfall"
        elif map_filter == 4:
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["population_capacity"]
                )
            self.selected_filter_name = "Population Capacity"
        elif map_filter == 5:
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["fertility"]
                )
            self.selected_filter_name = "Fertility"
        elif map_filter == 6:
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["traversal_cost"]
                )
            self.selected_filter_name = "Traversal Cost"
        elif map_filter == 7:
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["steepness"]
                )
            self.selected_filter_name = "Steepness"
        elif map_filter == 8:
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["population"]
                )
            self.selected_filter_name = "Population"
        elif map_filter == 9:
            display_map = view_data["colour"].copy()
            resource_map = view_data["resource"]
            for rid, color in config.RESOURCE_COLORS.items():
                display_map[resource_map == rid] = color
            self.selected_filter_name = "Resource"


        return display_map


    def draw_view(self, screen, display_map):
        """AI code using surfarray to draw the whole map at once."""
        surface = pygame.surfarray.make_surface(display_map.swapaxes(0, 1))  
        surface = pygame.transform.scale(surface, (display_map.shape[1] * config.CELL_SIZE,
                                                display_map.shape[0] * config.CELL_SIZE))
        screen.blit(surface, (config.SIDEBAR_WIDTH, 0))
    
    def draw_magnifier(self, screen, magnifier_map, hovered_cell, camera_x_pos, camera_y_pos):
        magnifier_surface = pygame.surfarray.make_surface(magnifier_map.swapaxes(0, 1))
        magnifier_surface = pygame.transform.scale(magnifier_surface, (magnifier_map.shape[1] * config.MAGNIFIER_CELL_SIZE,
                                                                          magnifier_map.shape[0] * config.MAGNIFIER_CELL_SIZE))
        screen.blit(magnifier_surface, ((hovered_cell[1]*config.CELL_SIZE)+config.SIDEBAR_WIDTH-(camera_x_pos*config.CELL_SIZE) - (config.MAGNIFIER_CELL_SIZE*magnifier_map.shape[1]//2),
                                        (hovered_cell[0]*config.CELL_SIZE)-camera_y_pos*config.CELL_SIZE - (config.MAGNIFIER_CELL_SIZE*magnifier_map.shape[0]//2)))

    def get_selected_filter_name(self):
        return self.selected_filter_name