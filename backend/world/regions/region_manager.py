from world.regions.region import Region
import numpy as np

class RegionManager:
    NO_REGION = 0xFFFF
    MAX_REGIONS_PER_CELL = 4

    def __init__(self, rows, cols, region_map=None, region_list=None):
        if region_map is not None:
            self.region_map = region_map
            self.region_list = region_list
            self.rid_counter = len(region_list)
        else:
            self.region_map = np.full(
                (rows, cols, self.MAX_REGIONS_PER_CELL), self.NO_REGION, dtype=np.uint16
            )
            self.region_list = []
            self.rid_counter = 0

    def get_region_map(self):
        return self.region_map

    def get_region_lookup(self):
        return [
            {
                "title": r["title"],
                "visible_desc": r["visible_desc"],
                "hidden_desc": r["hidden_desc"],
            }
            for r in self.region_list
        ]
    

    
    def create_region(self, title="", visible_desc="", hidden_desc=""):
        new_region = Region(self.rid_counter, title, visible_desc, hidden_desc)
        self.rid_counter += 1
        self.region_list.append(new_region)
        return new_region.rid

    def _add_at(self, y, x, rid):
        cell = self.region_map[y, x]
        if rid in cell:
            return
        empty = np.nonzero(cell == self.NO_REGION)[0]
        if empty.size:
            cell[empty[0]] = rid
        # else: cell is full, region silently dropped

    def add_region_with_mask(self, mask, rid):
        ys, xs = np.nonzero(mask)
        for y, x in zip(ys, xs):
            self._add_at(y, x, rid)

    def remove_region_with_mask(self, mask, rid):
        target = (self.region_map == rid) & mask[:, :, None]
        self.region_map[target] = self.NO_REGION

    def create_region_at_location(self, location, title, visible_desc, hidden_desc):
        rid = self.create_region(title, visible_desc, hidden_desc)
        self._add_at(location[0], location[1], rid)

    def get_regions_at_location(self, location):
        y, x = location
        cell = self.region_map[y, x]
        return [self.region_list[rid] for rid in cell[cell != self.NO_REGION]]



