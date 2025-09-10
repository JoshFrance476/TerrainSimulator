import pygame
from utils import config
from utils.overlay_generator import apply_heatmap_overlay

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""
    def __init__(self, controller):
        self.controller = controller
    
    def render_view(self, screen):
        '''Takes in world data and filter to produce display map, then draws to screen'''
        display_map = self.apply_overlay(self.controller.get_screen_data(), self.controller.selected_filter)
        self.draw_view(screen, display_map)
        
    
    def render_magnifier(self, screen):
        magnifier_display_map = self.apply_overlay(self.controller.get_magnifier_data(), self.controller.selected_filter)
        self.draw_magnifier(screen, magnifier_display_map, self.controller.hovered_cell, self.controller.get_camera_position())

    
    def apply_overlay(self, view_data, map_filter):
        '''Applies selected overlay to the base colour map.'''
        if map_filter == "None":
            display_map = view_data["colour"]
        elif map_filter == "Elevation":
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["elevation"]
                )
        elif map_filter == "Temperature":
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["temperature"]
                )
        elif map_filter == "Rainfall":
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["rainfall"]
                )
        elif map_filter == "Population Capacity":
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["population_capacity"]
                )
        elif map_filter == "Fertility":
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["fertility"]
                )
        elif map_filter == "Traversal Cost":
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["traversal_cost"]
                )
        elif map_filter == "Steepness":
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["steepness"]
                )
        elif map_filter == "Population":
            display_map = apply_heatmap_overlay(
                    view_data["coastline"],
                    view_data["population"]
                )
        elif map_filter == "Resource":
            display_map = view_data["colour"].copy()
            resource_map = view_data["resource"]
            for rid, color in config.RESOURCE_COLORS.items():
                display_map[resource_map == rid] = color
        elif map_filter == "State":
            display_map = view_data["colour"].copy()
            state_map = view_data["state"]
            for state_id, color in config.STATE_COLOURS.items():
                state_map_mask = state_map != 255
                display_map[state_map_mask & (state_map % len(config.STATE_COLOURS) == state_id)] = color
        return display_map


    def draw_view(self, screen, display_map):
        """AI code using surfarray to draw the whole map at once."""
        surface = pygame.surfarray.make_surface(display_map.swapaxes(0, 1))  
        surface = pygame.transform.scale(surface, (display_map.shape[1] * config.CELL_SIZE,
                                                display_map.shape[0] * config.CELL_SIZE))
        screen.blit(surface, (config.SIDEBAR_WIDTH, 0))
    
    def draw_magnifier(self, screen, magnifier_map, hovered_cell, camera_position):
        magnifier_surface = pygame.surfarray.make_surface(magnifier_map.swapaxes(0, 1))
        magnifier_surface = pygame.transform.scale(magnifier_surface, (magnifier_map.shape[1] * config.MAGNIFIER_CELL_SIZE,
                                                                          magnifier_map.shape[0] * config.MAGNIFIER_CELL_SIZE))
        screen.blit(magnifier_surface, ((hovered_cell[1]*config.CELL_SIZE)+config.SIDEBAR_WIDTH-(camera_position[0]*config.CELL_SIZE) - (config.MAGNIFIER_CELL_SIZE*magnifier_map.shape[1]//2),
                                        (hovered_cell[0]*config.CELL_SIZE)-camera_position[1]*config.CELL_SIZE - (config.MAGNIFIER_CELL_SIZE*magnifier_map.shape[0]//2)))

