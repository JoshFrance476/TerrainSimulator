from simulation.region import Region
from config import WORLD_COLS, WORLD_ROWS
import numpy as np

class RegionManager:
    def __init__(self):
        self.region_map = [[set() for _ in range(WORLD_COLS)] for _ in range(WORLD_ROWS)]
        self.region_list = []
        self.rid_counter = 0

    
    def create_region(self):
        new_region = Region(self.rid_counter)
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

    def get_region_map(self):
        return self.region_map
    
    def get_regions_at_location(self, location):
        y, x = location
        region_ids = self.region_map[y][x]

        return [self.region_list[rid] for rid in region_ids]

    def get_region(self, rid):
        return self.region_list[rid]


