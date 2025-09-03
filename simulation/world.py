from simulation.worldData import WorldData
from SettlementManager import SettlementManager
from utils.config import REGION_NAMES

class World:
    """Handles simulator and high level world logic."""

    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.data = WorldData(rows, cols)
        self.settlement_manager = SettlementManager(self.data.get_world_data())

        self.settlement_manager.init_settlements()

        
    
    def step(self):
        self.data.update()
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


    








    


