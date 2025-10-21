import pygame
import config
from rendering.overlay_generator import apply_heatmap_overlay
from utils.colour_utils import hsv_to_rgb_array
from skimage.color import label2rgb, rgb2hsv

class MapRenderer:
    """Handles rendering the terrain and overlays on the screen."""
    def __init__(self, controller):
        self.controller = controller
        self.display_maps = self.produce_display_maps(self.controller.get_world_data())
    
    def render_view(self, screen):
        '''Takes in world data and filter to produce display map, then draws to screen'''
        x0, y0, x1, y1 = self.controller.get_camera_boundaries()
        display_map = self.display_maps[self.controller.selected_filter][y0:y1,x0:x1]
        self.draw_view(screen, display_map)
        
    
    def render_magnifier(self, screen):
        x0, y0, x1, y1 = self.controller.get_magnifier_boundaries()
        magnifier_display_map = self.display_maps[self.controller.selected_filter][y0:y1,x0:x1]
        self.draw_magnifier(screen, magnifier_display_map, self.controller.hovered_cell, self.controller.get_camera_position())
    
    def produce_display_maps(self, world_data):
        display_maps = {
            'colour': world_data['colour'],
            'elevation': apply_heatmap_overlay(
                        world_data["coastline"],
                        world_data["elevation"]),
            'temperature': apply_heatmap_overlay(
                        world_data["coastline"],
                        world_data["temperature"]),
            'rainfall': apply_heatmap_overlay(
                        world_data["coastline"],
                        world_data["rainfall"]),
            'population_capacity': apply_heatmap_overlay(
                        world_data["coastline"],
                        world_data["population_capacity"]),
            'fertility': apply_heatmap_overlay(
                        world_data["coastline"],
                        world_data["fertility"]),
            'traversal_cost': apply_heatmap_overlay(
                        world_data["coastline"],
                        world_data["traversal_cost"]),
            'steepness': apply_heatmap_overlay(
                        world_data["coastline"],
                        world_data["steepness"]),
            'population': apply_heatmap_overlay(
                        world_data["coastline"],
                        world_data["population"]),
            'resource': self.produce_resource_display_map(
                        world_data['colour'].copy(),
                        world_data['resource']),
            'state': self.produce_state_display_map(
                        world_data['colour'].copy(),
                        world_data['state']),
            'landmass': self.produce_label_display_map(
                        world_data['colour'].copy(),
                        world_data['landmass_label']),
            'water_body': self.produce_label_display_map(
                        world_data['colour'].copy(),
                        world_data['water_body_label']),
            'continent': self.produce_label_display_map(
                        world_data['colour'].copy(),
                        world_data['continent_label']),
            'land_feature': self.produce_label_display_map(
                        world_data['colour'].copy(),
                        world_data['land_feature_label']),
            'ocean': self.produce_label_display_map(
                        world_data['colour'].copy(),
                        world_data['ocean_label']),
            'water_feature': self.produce_label_display_map(
                        world_data['colour'].copy(),
                        world_data['water_feature_label'])
        }

        return display_maps

    
    def produce_resource_display_map(self, colour_map, resource_map):
        resource_display_map = colour_map
        resource_map = resource_map
        for rid, color in config.RESOURCE_COLORS.items():
            resource_display_map[resource_map == rid] = color
        return resource_display_map

    def produce_state_display_map(self, colour_map, state_map):
        state_display_map = colour_map
        for state_id, color in config.STATE_COLOURS.items():
            state_map_mask = state_map != 255
            state_display_map[state_map_mask & (state_map % len(config.STATE_COLOURS) == state_id)] = color
        return state_display_map
    
    def produce_label_display_map(self, colour_map, label_map):
        landmass_display_map = rgb2hsv(label2rgb(label_map))
        landmass_display_map[..., 0] *= 360.0
        mask = label_map != 0
        colour_map[mask] = landmass_display_map[mask]
        return colour_map

    def draw_view(self, screen, display_map):
        """AI code using surfarray to draw the whole map at once."""
        rgb_map = hsv_to_rgb_array(display_map)

        surface = pygame.surfarray.make_surface(rgb_map.swapaxes(0, 1))
        surface = pygame.transform.scale(surface, (rgb_map.shape[1] * config.CELL_SIZE, 
                                                rgb_map.shape[0] * config.CELL_SIZE))
        screen.blit(surface, (config.SIDEBAR_WIDTH, 0))
    
    def draw_magnifier(self, screen, magnifier_map, hovered_cell, camera_position):
        rgb_map = hsv_to_rgb_array(magnifier_map)
        magnifier_surface = pygame.surfarray.make_surface(rgb_map.swapaxes(0, 1))
        magnifier_surface = pygame.transform.scale(magnifier_surface, (rgb_map.shape[1] * config.MAGNIFIER_CELL_SIZE,
                                                                          rgb_map.shape[0] * config.MAGNIFIER_CELL_SIZE))
        screen.blit(magnifier_surface, ((hovered_cell[1]*config.CELL_SIZE)+config.SIDEBAR_WIDTH-(camera_position[0]*config.CELL_SIZE) - (config.MAGNIFIER_CELL_SIZE*magnifier_map.shape[1]//2),
                                        (hovered_cell[0]*config.CELL_SIZE)-camera_position[1]*config.CELL_SIZE - (config.MAGNIFIER_CELL_SIZE*magnifier_map.shape[0]//2)))

