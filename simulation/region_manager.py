from simulation.region import Region
from config import WORLD_COLS, WORLD_ROWS
import numpy as np

class RegionManager:
    def __init__(self):
        self.region_map = np.zeros((WORLD_ROWS, WORLD_COLS), dtype=np.uint64)
        self.region_list = []
        self.rid_counter = 0

    
    def create_region(self):
        new_region = Region(self.rid_counter)
        self.rid_counter += 1
        self.region_list.append(new_region)
        return new_region.rid

    def add_region_with_mask(self, mask, rid):
        bit = np.uint64(1) << np.uint64(rid)
        self.region_map[mask] |= bit
    
    def remove_region_with_mask(self, mask, rid):
        bit = np.uint64(1) << np.uint64(rid)
        clear = np.uint64(~bit)
        self.region_map[mask] &= clear

    def get_region_map(self):
        return self.region_map
    
    def get_regions_at_location(self, location):
        mask = self.region_map[location]
        region_list = []
        bit = 0
        while mask:
            if mask & 1:
                region_list.append(self.region_list[bit])
            mask >>= 1
            bit += 1
        return region_list

    def get_region(self, rid):
        return self.region_list[rid]


