# state_manager.py
import numpy as np
from entities.State import State
from utils.config import NUMBER_OF_CITIES, CITIES_MIN_DISTANCE
from find_top_desiribility import find_top_desiribility_points

class StateManager:
    """Manages the collection of states in the simulation."""
    
    def __init__(self, population_map):
        self.states = []
        self.population_map = population_map
        self.initialize_states()

    def initialize_states(self):
        """Finds the best locations for states and creates them."""
        state_locations = find_top_desiribility_points(self.population_map, NUMBER_OF_CITIES, CITIES_MIN_DISTANCE)

        for (_, (r, c)) in state_locations:
            new_state = State((r, c))
            self.states.append(new_state)

    def update_states(self, sea_map, river_map, traversal_cost_map, population_map):
        """Updates all states, allowing them to expand and interact."""
        id_map = self.get_global_apid_territory_map()
        
        for state in self.states:
            state.update_aps(sea_map, river_map, traversal_cost_map, population_map, id_map)

    def get_global_apid_territory_map(self):
        """Generates a 2D map indicating the anchor ID of each occupied cell."""
        global_map = np.zeros_like(self.population_map, dtype=int)

        for state in self.states:
            state_map = state.get_apid_territory_map()
            global_map[state_map != 0] = state_map[state_map != 0]

        return global_map

    def get_global_sid_territory_map(self):
        """Generates a 2D map indicating the state ID of each occupied cell."""
        global_map = np.zeros_like(self.population_map, dtype=int)

        for state in self.states:
            state_map = state.get_sid_territory_map()
            global_map[state_map != 0] = state_map[state_map != 0]

        return global_map
