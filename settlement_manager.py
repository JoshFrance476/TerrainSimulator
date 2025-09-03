from settlement import Settlement
from utils.config import STARTING_SETTLEMENT_COUNT

class SettlementManager:
    def __init__(self, world, world_data):
        self.world = world
        self.world_data = world_data
        self.settlements = {}
        self.next_settlement_id = 0

        # Initialize settlements at the x largest values in the population map
        top_x_indices = self.world.get_x_largest_values("population", STARTING_SETTLEMENT_COUNT)
        for i, index in enumerate(top_x_indices):
            self.create_settlement(f"Settlement {i}", index[0], index[1])
    
    def update(self):
        for s in self.settlements.values():
            s.update()



    def create_settlement(self, name, r, c):
        id = self.next_settlement_id
        self.next_settlement_id += 1
        new_settlement = Settlement(id, name, r, c, self.world_data)
        self.settlements[id] = new_settlement
    
    
    def get_all_settlements(self):
        return self.settlements

    def get_settlement_by_pos(self, pos):
        for s in self.settlements.values():            
            if s.r == pos[0] and s.c == pos[1]:
                return s
        return None