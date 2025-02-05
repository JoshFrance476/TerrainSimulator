from collections import deque
import numpy as np
import config
from heapq import heappop, heappush

class AnchorPoint:
    """Represents region anchors in the simulation with location, prosperity, and territory."""
    
    # Class-level shared attributes
    anchor_list = []  # Stores all anchor instances
    traversal_cost_map = None
    sea_map = None
    river_map = None
    population_map = None
    can_expand = True
    anchor_uid_map = np.zeros((config.ROWS, config.COLS), dtype=int)  # Territory ownership map

    # Shared color palette for anchors
    colour_palette = [
        (180, 0, 0),   # Red
        (0, 180, 0),   # Green
        (0, 0, 180),   # Blue
        (180, 180, 0), # Yellow
        (180, 120, 0), # Orange
        (80, 0, 80),   # Purple
        (0, 180, 180), # Cyan
        (180, 20, 100) # Pink
    ]
    colour_index = 0  # Tracks assigned colors

    def __init__(self, location, uid, name="Unknown"):
        """Initializes a anchor with a location, territory_size, and a unique ID."""
        self.location = location  # (row, col) tuple
        self.name = name
        self.uid = uid
        self.territory = []
        self.colour = self.assign_unique_colour()
        self.type = 1

        AnchorPoint.anchor_list.append(self)  # Register anchor instance

    # ───────────────────────────────────── #
    #      CLASS-LEVEL INITIALIZATION       #
    # ───────────────────────────────────── #
    
    @classmethod
    def initialise(cls, traversal_cost_map, sea_map, river_map):
        """Initializes shared maps before anchor instances are created."""
        cls.traversal_cost_map = traversal_cost_map
        cls.sea_map = sea_map
        cls.river_map = river_map

    # ───────────────────────────────────── #
    #            GETTER METHODS             #
    # ───────────────────────────────────── #
    
    @classmethod
    def get_anchors(cls):
        """Returns a list of all created anchor."""
        return cls.anchor_list

    @classmethod
    def get_uid_map(cls):
        """Returns the global anchor UID map showing anchor territories."""
        return cls.anchor_uid_map

    def get_territory(self):
        """Returns the territory owned by the anchor."""
        return self.territory
    
    def get_colour(self):
        """Returns the anchor's assigned color."""
        return self.colour
    
    def get_location(self):
        """Returns the anchor's (row, col) location."""
        return self.location
    
    def get_uid(self):
        """Returns the anchor's unique identifier."""
        return self.uid
    
    def update_territory_size(self):
        """Increases the anchor's territory size by 1."""
        if self.can_expand:
            lowest_neighbouring_cell = self.find_lowest_cost_unclaimed_cell(self.location)
            if lowest_neighbouring_cell and len(self.territory) < config.CITY_MAX_TERRITORY:
                self.territory.append(lowest_neighbouring_cell)
            else:
                self.can_expand = False


    # ───────────────────────────────────── #
    #        TERRITORY & MAP LOGIC          #
    # ───────────────────────────────────── #
    
    @classmethod
    def generate_territory_uid_map(cls):
        """
        Generates a 2D UID map where each cell is assigned a anchor UID.
        Anchor points are marked with -1.

        Returns:
            numpy array: Territory map with anchor UIDs.
        """
        cls.anchor_uid_map.fill(0)  # Reset UID map

        for anchor in cls.anchor_list:
            for (r, c) in anchor.get_territory():
                cls.anchor_uid_map[r, c] = anchor.get_uid()

            # Mark anchor point with -1
            r, c = anchor.location
            cls.anchor_uid_map[r, c] = -1


    def assign_unique_colour(self):
        """Assigns a unique color to each anchor from the predefined list."""
        color = AnchorPoint.colour_palette[AnchorPoint.colour_index % len(AnchorPoint.colour_palette)]
        AnchorPoint.colour_index += 1
        return color


    def find_lowest_cost_unclaimed_cell(self, location):
        """Finds the lowest traversal cost unclaimed cell from the given location."""
        rows, cols = AnchorPoint.traversal_cost_map.shape
        start_r, start_c = location

        min_heap = [(AnchorPoint.traversal_cost_map[start_r, start_c], start_r, start_c)]  # (cost, row, col)
        visited = set()

        while min_heap:
            cost, r, c = heappop(min_heap)

            if (r, c) in visited:
                continue
            visited.add((r, c))

            cell_uid = AnchorPoint.get_uid_map()[r][c]
            # Check if this is an unclaimed cell
            if cell_uid == 0 and AnchorPoint.sea_map[r][c] == False and AnchorPoint.river_map[r][c] == False:
                return (r, c)  # Found the lowest-cost unclaimed cell

            #Only add neighbours if they are adjacent to city center or claimed cell
            if cell_uid == self.get_uid() or cell_uid == -1:
                # Add valid neighbors to the heap
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                        heappush(min_heap, (AnchorPoint.traversal_cost_map[nr, nc]+ cost, nr, nc))

        return None  # No valid unclaimed cell found



