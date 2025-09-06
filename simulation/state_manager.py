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
        new_state_map = self.update_all_state_territories_fast({1:0.2, 2:0.5, 3:0.8, 4:1.0})

        self._world.set_map_data("state", new_state_map)

        for state in self.states.values():
            state.tile_capacity = len(list(self._world.get_settlements_in_state(state.id))) * 100


    def create_state(self, name, r, c):
        new_state = State(self.next_state_id, name)
        self.next_state_id += 1

        self._world.set_map_data_at("state", (r, c), new_state.id)

        self.states[new_state.id] = new_state

        return new_state
    
    def expand_all_states(self, flip_rules, unclaimed_id=255):
        """
        Expand territory for all states simultaneously.
        
        state_map: 2D array of ints (state IDs, or `unclaimed_id` for unclaimed)
        traversal_cost_map: 2D float array
        flip_rules: dict {neighbor_count: base_prob} 
                    e.g. {1:0.1, 2:0.2, 3:0.5, 4:1.0}
        """

        state_map = self._world.get_map_data("state")
        traversal_cost_map = self._world.get_map_data("traversal_cost")
        region_map = self._world.get_map_data("region")

        rows, cols = state_map.shape
        new_map = state_map.copy()


        # --- Step 1: For each state, build adjacency counts ---
        unique_states = np.unique(state_map[state_map != unclaimed_id])


        # Store candidate flips as (prob, state_id)
        flip_probs = np.zeros((rows, cols), dtype=np.float32)
        flip_states = np.full((rows, cols), 255, dtype=np.int32)

        kernel = np.array([[0,1,0],
                        [1,0,1],
                        [0,1,0]])

        for sid in unique_states:
            state_mask = (state_map == sid).astype(np.int8)

            # Count neighbors of sid
            neighbor_count_map = convolve2d(state_mask, kernel, mode="same", boundary="fill")

            # Candidate tiles: unclaimed with sid neighbors
            unclaimed_neighbour_mask = (state_map == unclaimed_id) & (neighbor_count_map > 0) & (region_map != 0)

            # Lookup base prob from rules
            base_prob = np.zeros_like(neighbor_count_map, dtype=np.float32)

            for n, p in flip_rules.items():
                base_prob[neighbor_count_map == n] = p

            # Adjust for traversal cost
            prob = base_prob / np.clip(traversal_cost_map, 1, 10)

            prob[traversal_cost_map > 10] = 0

            # Roll dice for sid
            rolls = np.random.rand(*state_map.shape)
            flips = (rolls < prob) & unclaimed_neighbour_mask

            # Conflict resolution: keep higher prob
            better = flips & (prob > flip_probs)
            flip_probs[better] = prob[better]
            flip_states[better] = sid

        # --- Step 2: Apply flips ---
        new_map[state_map == unclaimed_id] = np.where(
            flip_states[state_map == unclaimed_id] != 255,
            flip_states[state_map == unclaimed_id],
            new_map[state_map == unclaimed_id]
        )

        return new_map

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
        claimed_mask = (neighbor_stack != unclaimed_id) | water_stack

        neighbor_counts = claimed_mask.sum(axis=0)


        decay_prob = np.zeros_like(state_map, dtype=np.float32)

        decay_prob = (settlement_dist_map * 0.002)

        decay_prob[neighbor_counts == 4] = 0

        decay_prob[neighbor_counts == 3] = 0


        rolls = np.random.rand(rows, cols)
        flips = (rolls < decay_prob) & (state_map != unclaimed_id)

        new_map[flips] = unclaimed_id

        # Base probabilities from flip_rules (array lookup by count)
        base_prob = np.zeros_like(state_map, dtype=np.float32)
        for n, p in flip_rules.items():
            base_prob[neighbor_counts == n] = p

        # Scale by traversal cost
        prob = base_prob / (traversal_cost_map - 1)


        # Candidate mask: unclaimed cells with at least one neighbor and valid region
        candidates = (state_map == unclaimed_id) & (neighbor_counts > 0) & (region_map != 0)

        # For each candidate, pick a neighbor state id
        # (use the first non-unclaimed neighbor; could randomize if you prefer)
        neighbor_ids = np.full_like(state_map, unclaimed_id, dtype=np.int32)
        for direction in range(4):
            mask = candidates & (neighbor_ids == unclaimed_id) & (neighbor_stack[direction] != unclaimed_id)
            neighbor_ids[mask] = neighbor_stack[direction][mask]
        
        for state in self.states.values():
            state_tiles = np.sum(state_map == state.id)
            factor = max(0.0, 1 - state_tiles / state.tile_capacity)
            state.tile_count = state_tiles
            prob[neighbor_ids == state.id] *= factor

        # Roll dice once
        rolls = np.random.rand(rows, cols)
        flips = candidates & (rolls < prob) & (neighbor_ids != unclaimed_id)

        # Apply flips
        new_map[flips] = neighbor_ids[flips]

        return new_map
    
    def get_all_states(self):
        return self.states


