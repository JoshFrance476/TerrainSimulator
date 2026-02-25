from simulation.region import Region
from config import WORLD_COLS, WORLD_ROWS

class RegionManager:
    def __init__(self):
        self.region_map = [[[] for x in range(WORLD_COLS)] for y in range(WORLD_ROWS)] 
        self.region_list = []
        self.rid_counter = 0

    
    def create_region(self):
        new_region = Region(self.rid_counter)
        self.rid_counter += 1
        self.region_list.append(new_region)
        return new_region.rid

    def add_region_to_location(self, location, rid):
        grid_address = self.region_map[location[0]][location[1]]
        if rid not in grid_address:
            grid_address.append(rid)
    
    def get_region_map(self):
        return self.region_map
    
    def get_regions_at_location(self, location):
        region_list = []
        grid_address = self.region_map[location[0]][location[1]]
        for rid in grid_address:
            region = self.region_list[rid]
            region_list.append(region)
        return region_list

    def get_region(self, rid):
        return self.region_list[rid]


