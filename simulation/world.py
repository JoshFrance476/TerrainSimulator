from simulation.world_data import WorldData
from settlement_manager import SettlementManager
from utils.config import REGION_NAMES

class World:
    """Handles simulator and high level world logic."""

    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.data = WorldData(rows, cols)
        self.settlement_manager = SettlementManager(self, self.data.get_world_data())


        
    
    def step(self, tick_count):
        if tick_count % 60 == 0:
            self.settlement_manager.update()

    #def update(self):
        #self.dynamic_maps = update_dynamic_maps(self.static_maps_dict, self.dynamic_maps_dict)
    
    def get_world_data(self):
        return self.data.get_world_data()  
    
    def get_region_data(self, x0, y0, x1, y1):
        return self.data.get_region_data(x0, y0, x1, y1)
    
    def get_settlement_by_pos(self, pos):
        return self.settlement_manager.get_settlement_by_pos(pos)

    def get_all_settlements(self):
        return self.settlement_manager.get_all_settlements()


    def get_cell_data(self, selected_cell):
        if selected_cell:
            return self.data.get_cell_data(selected_cell), self.settlement_manager.get_settlement_by_pos(selected_cell)
        else:
            return None, None
    

    def get_surrounding_data(self, r, c, radius=3, map="all"):
        r0, r1 = max(0, r-radius), min(self.rows, r+radius+1)
        c0, c1 = max(0, c-radius), min(self.cols, c+radius+1)

        if map == "all":
            return self.data.get_region_data(c0, r0, c1, r1)
        else:
            return self.data.get_region_data(c0, r0, c1, r1)[map]


    def get_x_largest_values(self, map_name, x):
        return self.data.find_x_largest_values(map_name, x)

    








    


