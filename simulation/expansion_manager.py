# expansion_manager.py
import numpy as np
from heapq import heappop, heappush

class ExpansionManager:
    """Handles state expansion by managing anchor points' territory growth."""
    
    def __init__(self, sea_map, river_map, traversal_cost_map, population_map):
        self.sea_map = sea_map
        self.river_map = river_map
        self.traversal_cost_map = traversal_cost_map
        self.population_map = population_map

    def expand_anchor_point(self, anchor, id_map):
        """Expands an anchor point by claiming the lowest-cost unclaimed cell."""
        location = anchor.get_location()
        new_cell = self._find_lowest_cost_unclaimed_cell(location, id_map)

        if new_cell:
            anchor.territory.append(new_cell)
        else:
            anchor.can_expand = False  # Mark as fully expanded

    def _find_lowest_cost_unclaimed_cell(self, location, id_map):
        """Finds the lowest traversal cost unclaimed cell near the anchor point."""
        rows, cols = self.traversal_cost_map.shape
        start_r, start_c = location

        min_heap = [(self.traversal_cost_map[start_r, start_c], start_r, start_c)]
        visited = set()

        while min_heap:
            cost, r, c = heappop(min_heap)

            if (r, c) in visited or id_map[r][c] != 0:
                continue
            visited.add((r, c))

            # Ensure it's a valid expansion target (not sea or river)
            if not self.sea_map[r, c] and not self.river_map[r, c]:
                return (r, c)

            # Add neighbors for expansion consideration
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    heappush(min_heap, (self.traversal_cost_map[nr, nc] + cost, nr, nc))

        return None  # No valid expansion cell found

    def create_friendly_neighbor(self, anchor, state_id, id_map):
        """Attempts to create a new anchor in a high-population area near an existing one."""
        border_cells = anchor.get_border_proximity_cells(8, id_map, self.sea_map, self.river_map)

        valid_indices = np.where(border_cells)
        valid_values = self.population_map[valid_indices]

        if valid_values.size == 0:
            return None  # No valid location

        max_index = np.argmax(valid_values)
        new_location = (valid_indices[0][max_index], valid_indices[1][max_index])

        return new_location
