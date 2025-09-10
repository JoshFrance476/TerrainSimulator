from simulation.settlement import Settlement
from utils.config import STARTING_SETTLEMENT_COUNT, RESOURCE_NAMES, SETTLEMENT_LIMIT
from scipy.ndimage import distance_transform_edt
import numpy as np

class SettlementManager:
    def __init__(self, world):
        self._world = world
        self.settlements = {}
        self.next_settlement_id = 0

        # Initialize settlements at the x largest values in the population map
        top_x_indices = self._world.get_x_largest_values("population", STARTING_SETTLEMENT_COUNT)
        for i, index in enumerate(top_x_indices):
            self.create_settlement(index[0], index[1], f"Settlement {i}")
    
    def update(self):
        for s in self.settlements.values():
            s.update()
    

    def create_settlement(self, r, c, name="Unnamed"):
        id = self.next_settlement_id
        self.next_settlement_id += 1

        new_settlement = Settlement(id, name, r, c, self._world)

        self.settlements[id] = new_settlement


    def find_eligible_settlements(self):
        population_map = self._world.get_map_data("population")
        settlement_distance_map = self._world.get_map_data("settlement_distance")
        eligible_settlements = np.where((population_map > 3) & (settlement_distance_map > 10))
        for r, c in zip(eligible_settlements[0], eligible_settlements[1]):
            self.create_settlement(f"Settlement {len(self.settlements)}", r, c)
        
    
    def create_settlement_distance_map(self, r, c):
        mask = np.ones((r, c), dtype=bool)  
        for s in self.settlements.values():
            mask[s.r, s.c] = False
        return distance_transform_edt(mask)

    
    def get_all_settlements(self):
        return self.settlements

    def get_settlement_by_pos(self, pos):
        for s in self.settlements.values():            
            if s.r == pos[0] and s.c == pos[1]:
                return s
        return None
    
    def find_eligible_state_founders(self):
        for s in self.settlements.values():
            if s.population > 5:
                yield s