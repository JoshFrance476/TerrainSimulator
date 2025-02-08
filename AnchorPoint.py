import numpy as np
import config
from heapq import heappop, heappush
from scipy.ndimage import binary_dilation

class AnchorPoint:
    """Represents region anchors in the simulation with location, prosperity, and territory."""
    
    # Class-level shared attributes
    id_counter = 1


    def __init__(self, location, sid = -1, name="Unknown"):
        """Initializes a anchor with a location, territory_size, and a unique ID."""
        self.location = location  # (row, col) tuple
        self.name = name

        self.id = AnchorPoint.id_counter
        AnchorPoint.id_counter += 1

        self.territory = []
        self.type = 1
        self.can_expand = True


        if sid == -1:       #if sid is not provided, assume creation of a new state with apid as sid
            self.sid == self.id
        else:
            self.sid = sid
            


    # ───────────────────────────────────── #
    #            GETTER METHODS             #
    # ───────────────────────────────────── #
    


    def get_territory(self):
        """Returns the territory owned by the anchor."""
        return self.territory
    
    
    def get_location(self):
        """Returns the anchor's (row, col) location."""
        return self.location
    
    def get_id(self):
        """Returns the anchor's unique identifier."""
        return self.id
    
    def update_territory_size(self, sea_map, river_map, traversal_cost_map, population_map, id_map):
        """Increases the anchor's territory size by 1."""
        lowest_neighbouring_cell = self.find_lowest_cost_unclaimed_cell(self.location, sea_map, river_map, traversal_cost_map, id_map)
        if lowest_neighbouring_cell:
            self.territory.append(lowest_neighbouring_cell)
        else:
            print("no valid cell found")



    # ───────────────────────────────────── #
    #        TERRITORY & MAP LOGIC          #
    # ───────────────────────────────────── #
    



    def find_lowest_cost_unclaimed_cell(self, location, sea_map, river_map, traversal_cost_map, id_map):
        """Finds the lowest traversal cost unclaimed cell from the given location."""
        rows, cols = traversal_cost_map.shape
        start_r, start_c = location

        min_heap = [(traversal_cost_map[start_r, start_c], start_r, start_c)]  # (cost, row, col)
        visited = set()

        while min_heap:
            cost, r, c = heappop(min_heap)

            cell_id = id_map[r][c]

            if (r, c) in visited:
                continue
            visited.add((r, c))


            
            # Check if this is an unclaimed cell
            if cell_id == 0 and sea_map[r][c] == False and river_map[r][c] == False:
                return (r, c)  # Found the lowest-cost unclaimed cell

            #Only add neighbours if they are adjacent to city center or claimed cell
            if cell_id == self.id or (cell_id == -1 and (r, c) == self.location):
                # Add valid neighbors to the heap
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                        heappush(min_heap, (traversal_cost_map[nr, nc]+ cost, nr, nc))

        return None  # No valid unclaimed cell found
    
    def get_border_proximity_cells(self, proximity, id_map, sea_map, river_map):

        # uid_mask is a boolean map of just self's territory, including city center
        id_mask = (id_map == self.id)  # Create mask based on self.id
        id_mask[self.location] = True  # Ensure (row, col) is explicitly set to True


        # Create a structuring element (cross shape) for checking adjacent cells
        structuring_element = np.array([[0,1,0], [1,1,1], [0,1,0]])  # 4-way connectivity

        # Expand territory area by proximity to find proximity cells
        border_proximity_cells = binary_dilation(id_mask, structuring_element, proximity)
        border_min_proximity_cells = binary_dilation(id_mask, structuring_element, proximity-3)

        border_proximity_cells = border_proximity_cells & (id_map == 0) & ~sea_map & ~border_min_proximity_cells

        #something about this conversion isn't right. Border proximity cells should be up to n away from ap borders, excluding where id map isn't 0 (so only unclaimed territory)

        return border_proximity_cells

    def create_friendly_neighbour(self, sid, population_map, id_map, sea_map, river_map):
        proximate_cells = self.get_border_proximity_cells(8, id_map, sea_map, river_map)

        # Get the indices of the cells within the proximity
        valid_indices = np.where(proximate_cells)

        # Extract the population values for those indices
        valid_values = population_map[valid_indices]

        if valid_values.size == 0:
            return None  # No valid cells to expand into
        max_index = np.argmax(valid_values)  # Position in the flattened valid values
        max_value = valid_values[max_index]  # Max value itself

        # Retrieve the corresponding (row, col) location
        new_location = (valid_indices[0][max_index], valid_indices[1][max_index])

        print("creating neighbour at ", new_location)

        #self.can_expand = False

        return new_location


