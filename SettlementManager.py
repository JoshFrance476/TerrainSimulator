from Settlement import Settlement
from utils.map_utils import find_k_largest_value_locations

class SettlementManager:
    def __init__(self, data):
        self.data = data
        self.settlements = {}
        self.next_settlement_id = 0
    
    def update(self):
        pass
    
    def init_settlements(self):
        # Find the 10 largest values in the population map
        population_map = self.data["population"]
        top_10_indices = find_k_largest_value_locations(population_map, 10)
        print(top_10_indices)
        # Initialize settlements at these locations
        for index in top_10_indices:
            self.create_settlement("placeholder", index[0], index[1])
    

    def create_settlement(self, name, r, c):
        id = self.next_settlement_id
        self.next_settlement_id += 1
        new_settlement = Settlement(0, name, r, c)
        self.settlements[id] = new_settlement
    
    def get_settlement_data(self):
        return [
        {
            "id": s.id,
            "name": s.name,
            "pos": (s.r, s.c),
        }
        for s in self.settlements.values()
    ]