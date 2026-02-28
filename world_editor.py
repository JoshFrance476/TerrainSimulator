import pygame

class WorldEditor:
    def __init__(self, world, brush_manager, biome_config):
        self.world = world
        self.brush = brush_manager
        self.biome_config = biome_config
    
    def recompute_after_biome_change(self):
        self.world.update_stage_3()
    
    def recompute_after_elevation_change(self):
        self.world.update_steepness()
        self.world.update_biome()
        self.world.update_stage_3()
   
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
    
    def create_region(self):
        return self.world.create_region()
    
    def paint_region(self, location, rid):
        for brush_location in self.brush.get_brush(location):
            self.world.add_region_to_location(brush_location, rid)
    
    def remove_region(self, location, rid):
        for brush_location in self.brush.get_brush(location):
            self.world.remove_region_from_location(brush_location, rid)
    
    def set_painted_region_info(self, title, visible_desc, hidden_desc, region_id = None):
        if region_id is not None:
            region = self.world.region_manager.region_list[region_id]
        elif self.state.most_recent_region_paint != None:
            region = self.world.region_manager.region_list[self.state.most_recent_region_paint]
        region.title = title
        region.visible_desc = visible_desc
        region.hidden_desc = hidden_desc
    
    def add_biome(self, name, h, s, v, traversal_cost):
        self.biome_config.add_biome(name, h, s, v, traversal_cost)
        self.recompute_after_biome_change()
    
    def edit_biome(self, index, name, h, s, v, traversal_cost):
        self.biome_config.edit_biome(index, name, h, s, v, traversal_cost)
        self.recompute_after_biome_change()