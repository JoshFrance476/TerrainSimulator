from collections import deque
import numpy as np
import config

class AnchorPoint:
    """Represents region anchors in the simulation with location, prosperity, and territory."""
    
    # Class-level shared attributes
    anchor_list = []  # Stores all anchor instances
    traversal_cost_map = None
    sea_map = None
    river_map = None
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

    def __init__(self, location, territory_size, uid, name="Unknown"):
        """Initializes a anchor with a location, territory_size, and a unique ID."""
        self.location = location  # (row, col) tuple
        self.name = name
        self.uid = uid
        self.territory_size = territory_size
        self.territory = self.generate_territory(self.location, self.territory_size)  # List of (row, col) coordinates representing the anchor's territory
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
        if self.territory_size < config.CITY_MAX_TERRITORY:
            self.territory_size += 1
            self.territory = self.generate_territory(self.location, self.territory_size)

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

    def generate_territory(self, location, territory_size):
        """
        Assigns a 'territory' to this anchor based on the traversal cost map.

        Args:
            traversal_cost_map (numpy array): Movement cost for each cell.
            sea_map (numpy array): Boolean map of water locations.
            river_map (numpy array): Boolean map of river locations.
        """
        rows, cols = AnchorPoint.traversal_cost_map.shape
        start_r, start_c = location

        visited = set()
        queue = deque([(start_r, start_c, 0)])  # (row, col, cost)

        territory = []  # Initialise anchors's territory

        while queue:
            r, c, cost = queue.popleft()

            # Skip if already visited, exceeds prosperity limit, or is water
            if (r, c) in visited or cost > territory_size or AnchorPoint.sea_map[r][c] or AnchorPoint.river_map[r][c]:
                continue

            visited.add((r, c))
            territory.append((r, c))  # Add valid cell to territory

            # Explore 4 neighboring cells
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:  # Stay within bounds
                    next_cost = cost + (AnchorPoint.traversal_cost_map[nr, nc] * 2)
                    queue.append((nr, nc, next_cost))
        
        return territory

    