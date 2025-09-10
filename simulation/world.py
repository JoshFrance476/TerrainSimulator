from simulation.world_data import WorldData
from simulation.settlement_manager import SettlementManager
from simulation.state_manager import StateManager
from utils.config import REGION_NAMES

class World:
    """Handles simulator and high level world logic."""

    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.data = WorldData(rows, cols)
        self.settlement_manager = SettlementManager(self)
        self.state_manager = StateManager(self)

        for settlement in self.settlement_manager.get_all_settlements().values():
            if settlement.id%5 == 0:
                self.state_manager.create_state(settlement.r, settlement.c, f"State {settlement.id}")

        
    def step(self, tick_count):
        if tick_count % 30 == 0:
            self.data.update()
            self.settlement_manager.update()
            self.state_manager.update()
            

    
    def get_world_data(self):
        return self.data.get_world_data()  
    
    def get_map_data(self, map_name):
        return self.data.get_world_data()[map_name]
    
    def set_map_data(self, map_name, data):
        self.data.set_map_data(map_name, data)
    
    def set_map_data_at(self, map_name, pos, data):
        self.data.set_map_data_at(map_name, pos, data)
    
    def get_region_data(self, x0, y0, x1, y1):
        return self.data.get_region_data(x0, y0, x1, y1)
    
    def get_settlement_by_pos(self, pos):
        return self.settlement_manager.get_settlement_by_pos(pos)

    def get_all_settlements(self):
        return self.settlement_manager.get_all_settlements()
    
    def get_all_states(self):
        return self.state_manager.get_all_states()
    
    def get_settlement_distance_map(self):
        return self.settlement_manager.create_settlement_distance_map(self.rows, self.cols)


    def get_cell_data(self, selected_cell):
        if selected_cell:
            return self.data.get_cell_data(selected_cell), self.settlement_manager.get_settlement_by_pos(selected_cell), selected_cell
        else:
            return None, None, None
    

    def get_surrounding_data(self, r, c, radius=3, map="all"):
        r0, r1 = max(0, r-radius), min(self.rows, r+radius+1)
        c0, c1 = max(0, c-radius), min(self.cols, c+radius+1)

        if map == "all":
            return self.data.get_region_data(c0, r0, c1, r1)
        else:
            return self.data.get_region_data(c0, r0, c1, r1)[map]


    def get_x_largest_values(self, map_name, x):
        return self.data.find_x_largest_values(map_name, x)
    
    def get_settlements_in_state(self, state_id):
        for settlement in self.settlement_manager.get_all_settlements().values():
            if settlement.state == state_id:
                yield settlement
    

    
    def find_eligible_state_founders(self):
        return self.settlement_manager.find_eligible_state_founders()
    
    def create_settlement(self, r, c):
        return self.settlement_manager.create_settlement(r, c)

    def create_state(self, r, c):
        return self.state_manager.create_state(r, c)

    








    


