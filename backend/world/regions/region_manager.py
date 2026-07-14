from backend.world.regions.region import Region
import numpy as np

class RegionManager:
    def __init__(self, rows, cols, region_map=None, region_list=None, rid_counter=None):
        if region_map:
            self.region_map = region_map
            self.region_list = region_list
            self.rid_counter = rid_counter
        else:
            self.region_map = [[set() for _ in range(cols)] for _ in range(rows)]
            self.region_list = []
            self.rid_counter = 0

    
    def create_region(self, title="", visible_desc="", hidden_desc=""):
        new_region = Region(self.rid_counter, title, visible_desc, hidden_desc)
        self.rid_counter += 1
        self.region_list.append(new_region)
        return new_region.rid

    def add_region_with_mask(self, mask, rid):
        ys, xs = np.nonzero(mask)
        for y, x in zip(ys, xs):
            self.region_map[y][x].add(rid)
    
    def remove_region_with_mask(self, mask, rid):
        ys, xs = np.nonzero(mask)
        for y, x in zip(ys, xs):
            self.region_map[y][x].discard(rid)
    
    def create_region_at_location(self, location, title, visible_desc, hidden_desc):
        rid = self.create_region(title, visible_desc, hidden_desc)
        self.region_map[location[0]][location[1]].add(rid)

    def get_region_map(self):
        return self.region_map
    
    def get_regions_at_location(self, location):
        y, x = location
        region_ids = self.region_map[y][x]

        return [self.region_list[rid] for rid in region_ids]

    def get_region(self, rid):
        return self.region_list[rid]



