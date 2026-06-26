import pygame
from skimage.segmentation import flood_fill
from app_state import PaintMode

class WorldEditor:
    def __init__(self, world, brush_manager, state):
        self.world = world
        self.brush = brush_manager
        self.state = state

        self.paint_mode = PaintMode.BRUSH

        self.elevation_updates_biome = False
    
    def recompute_after_biome_change(self):
        self.world.update_steepness()
        self.world.update_stage_3()
    
    def recompute_after_elevation_change(self, mask):
        self.world.update_steepness()
        if self.elevation_updates_biome:
            self.world.update_biome(mask)
        self.world.update_stage_3()
   
    def paint_biome(self, location, biome_id):
        if self.paint_mode is PaintMode.BRUSH:
            self.world.set_biome_with_mask(self.brush.get_brush_mask(location), biome_id)
        elif self.paint_mode is PaintMode.FILL:
            self.world.set_map_data("biome", flood_fill(self.world.get_map_data("biome"), location, new_value=biome_id))
        self.recompute_after_biome_change()
    
    def edit_elevation(self, location, negative=False):
        if self.state.lctrl_down:
            brush_mask = self.brush.get_brush_mask(location)
            self.world.apply_smoothing_elevation_mask(brush_mask)
        else:
            brush_mask = self.brush.get_brush_mask(location, boolean = False, negative=negative)
            self.world.apply_edit_elevation_mask(brush_mask)
        self.recompute_after_elevation_change(brush_mask)
    
    def create_region(self):
        return self.world.create_region()
    
    def paint_region(self, location, rid):
        self.world.add_region_with_mask(self.brush.get_brush_mask(location), rid)
    
    def remove_region(self, location, rid):
        self.world.remove_region_with_mask(self.brush.get_brush_mask(location), rid)
    
    def add_region_to_location(self, location, rid):
        self.world.add_region_to_location(location, rid)
    
    def set_painted_region_info(self, title, visible_desc, hidden_desc, region_id):
        region = self.world.get_region(region_id)
        region.title = title
        region.visible_desc = visible_desc
        region.hidden_desc = hidden_desc
    
    def add_biome(self, name, h, s, v, traversal_cost, description):
        self.world.add_biome(name, h, s, v, traversal_cost, description)
        self.recompute_after_biome_change()
    
    def edit_biome(self, index, name, h, s, v, traversal_cost, description):
        self.world.edit_biome(index, name, h, s, v, traversal_cost, description)
        self.recompute_after_biome_change()
    
