from simulation.worldData import WorldData
from SettlementManager import SettlementManager

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
    
    def get_data_for_ui(self):
        return self.data.get_world_data(), self.settlement_manager.get_settlement_data()


    








    


