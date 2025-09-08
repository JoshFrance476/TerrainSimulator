from simulation.state import State
import random
import numpy as np
from scipy.signal import convolve2d

class StateManager:
    def __init__(self, world):
        self._world = world

        self.states = {}

        self.next_state_id = 0

    
    def update(self):
        new_state_map, prob, decay_prob, neighbor_counts, settlement_dist_map = self.update_all_state_territories_fast({1:0.05, 2:0.2, 3:0.95, 4:1.0})

        self._world.set_map_data("state", new_state_map)
        self._world.set_map_data("flip_probability", prob)
        self._world.set_map_data("decay_probability", decay_prob)
        self._world.set_map_data("neighbor_counts", neighbor_counts)
        self._world.set_map_data("settlement_distance", settlement_dist_map)


        for state in self.states.values():
            tile_capacity = 0
            for settlement in self._world.get_settlements_in_state(state.id):
                tile_capacity += settlement.population*60
            state.tile_capacity = tile_capacity

    def create_state(self, name, r, c):
        new_state = State(self.next_state_id, name)
        self.next_state_id += 1

        self._world.set_map_data_at("state", (r, c), new_state.id)

        self.states[new_state.id] = new_state

        return new_state
    
    
    def update_all_state_territories_fast(self, flip_rules, unclaimed_id=255):
        """
        Expand territory for all states simultaneously (optimized).
        """
        state_map = self._world.get_map_data("state")
        traversal_cost_map = self._world.get_map_data("traversal_cost")
        region_map = self._world.get_map_data("region")
        settlement_dist_map = self._world.get_settlement_distance_map()

        rows, cols = state_map.shape
        new_map = state_map.copy()

        # Precompute neighbor maps by shifting (north, south, west, east)
        north = np.roll(state_map, -1, axis=0)
        south = np.roll(state_map,  1, axis=0)
        west  = np.roll(state_map, -1, axis=1)
        east  = np.roll(state_map,  1, axis=1)

        neighbor_stack = np.stack([north, south, west, east], axis=0)

        # Build water neighbor stack aligned with neighbor_stack
        north_w = np.roll(region_map == 0, -1, axis=0)
        south_w = np.roll(region_map == 0,  1, axis=0)
        west_w  = np.roll(region_map == 0, -1, axis=1)
        east_w  = np.roll(region_map == 0,  1, axis=1)

        water_stack = np.stack([north_w, south_w, west_w, east_w], axis=0)

        # A neighbor is "blocking" if it's claimed OR water
        claimed_mask_with_water = (neighbor_stack != unclaimed_id) | water_stack
        claimed_mask = (neighbor_stack != unclaimed_id)

        neighbor_counts_with_water = claimed_mask_with_water.sum(axis=0)
        neighbor_counts = claimed_mask.sum(axis=0)


        

        

        


        # Candidate mask: unclaimed cells with at least one neighbor and valid region
        candidates = (state_map == unclaimed_id) & (neighbor_counts_with_water > 0) & (region_map != 0)

        # For each candidate, pick a neighbor state id
        # (use the first non-unclaimed neighbor; could randomize if you prefer)
        neighbor_ids = np.full_like(state_map, unclaimed_id, dtype=np.int32)
        for direction in range(4):
            mask = candidates & (neighbor_ids == unclaimed_id) & (neighbor_stack[direction] != unclaimed_id)
            neighbor_ids[mask] = neighbor_stack[direction][mask]





        decay_prob = np.zeros_like(state_map, dtype=np.float32)

        decay_prob = (settlement_dist_map**2) * 0.0001
        #decay_prob = np.clip(decay_prob, 0, 1)


        # Base probabilities from flip_rules (array lookup by count)
        base_prob = np.zeros_like(state_map, dtype=np.float32)
        for n, p in flip_rules.items():
            base_prob[neighbor_counts_with_water == n] = p

        
        for state in self.states.values():
            state_tiles = np.sum(state_map == state.id)
            factor = max(0.0, 1 - state_tiles / state.tile_capacity)
            state.tile_count = state_tiles
            base_prob[neighbor_ids == state.id] *= factor
            decay_prob[neighbor_ids == state.id] *= factor
        

        min_cost, max_cost = 1, 3
        clipped = np.clip(traversal_cost_map, min_cost, max_cost)
        multiplier = (max_cost - clipped) / (max_cost - min_cost)
        base_prob *= multiplier




        decay_prob[neighbor_counts_with_water == 4] = 0

        decay_prob[(neighbor_counts == 0) & (settlement_dist_map > 0)] = 1


        rolls = np.random.rand(rows, cols)
        flips = (rolls < decay_prob) & (state_map != unclaimed_id)

        new_map[flips] = unclaimed_id



        #base_prob = base_prob / (traversal_cost_map - 1)

        
        base_prob[neighbor_counts_with_water == 4] = 1

        # Roll dice once
        rolls = np.random.rand(rows, cols)
        flips = candidates & (rolls < base_prob) & (neighbor_ids != unclaimed_id)

        # Apply flips
        new_map[flips] = neighbor_ids[flips]

        return new_map, base_prob, decay_prob, neighbor_counts_with_water, settlement_dist_map
    
    def get_all_states(self):
        return self.states


