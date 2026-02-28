import pygame

class WorldEditor:
    def __init__(self, world, brush_manager, map_renderer_refresh_function):
        self.world = world
        self.brush = brush_manager
        self.refresh_render = map_renderer_refresh_function
    
    def recompute_after_biome_change(self):
        self.world.update_stage_3()
        self.refresh_render()
    
    def recompute_after_elevation_change(self):
        self.world.update_steepness()
        self.world.update_biome()
        self.world.update_stage_3()
        self.refresh_render()
    
    def paint_tile(self, location, tid):
        for brush_location in self.brush.get_brush(location):
            self.world.set_map_data_at("biome", brush_location, tid)
        self.recompute_after_biome_change()
    
    def edit_elevation(self, location, negative=False):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL]:
            self.world.apply_smoothing_elevation_mask(self.brush.get_brush_mask(location, True))
        else:
            if negative:
                self.brush.brush_strength = -0.02
            else:
                self.brush.brush_strength = 0.02
            self.world.apply_edit_elevation_mask(self.brush.get_brush_mask(location))
        self.recompute_after_elevation_change()
    
    def paint_region(self, location, rid):
        for brush_location in self.brush.get_brush(location):
            self.world.add_region_to_location(brush_location, rid)
        self.refresh_render()
    
    def remove_region(self, location, rid):
        for brush_location in self.brush.get_brush(location):
            self.world.remove_region_from_location(brush_location, rid)
        self.refresh_render()