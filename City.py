from collections import deque

class City:
    # Shared class-level color palette (avoids storing in each instance)
    colour_palette = [
        (180, 0, 0),   # Red
        (0, 180, 0),   # Green
        (0, 0, 180),   # Blue
        (180, 180, 0), # Yellow
        (180, 120, 0), # Orange
        (80, 0, 80), # Purple
        (0, 180, 180), # Cyan
        (180, 20, 100) # Pink
    ]
    colour_index = 0  # Shared index to track assigned colors

    def __init__(self, location, prosperity, name="Unknown"):
        self.location = location
        self.name = name
        self.territory = []  # List of (row, col) coordinates that belong to the city
        self.colour = self.assign_unique_colour()
        self.prosperity = prosperity

    def __str__(self):
        return f"City {self.name} at {self.location}, Territory size: {len(self.territory)}"
    
    def get_territory(self):
        return self.territory
    
    def get_colour(self):
        return self.colour
    
    def get_location(self):
        return self.location
    
    def assign_unique_colour(self):
        """Assigns a color from the predefined class-level list."""
        color = City.colour_palette[City.colour_index % len(City.colour_palette)]
        City.colour_index += 1  # Move to the next color for the next city
        return color
    

    def generate_territory(self, traversal_cost_map, sea_map):
        """
        Assigns a 'territory' to this city based on the traversal cost map.

        Args:
            traversal_cost_map (numpy array): 2D array where each cell represents the cost to traverse.
            max_cost (int): Maximum traversal cost allowed for this city's territory.

        Returns:
            None: This city object updates its 'territory' attribute.
        """
        rows, cols = traversal_cost_map.shape
        start_r, start_c = self.location

        visited = set()
        queue = deque([(start_r, start_c, 0)])  # (row, col, current_cost)

        self.territory = []  # Reset the city's territory

        while queue:
            r, c, cost = queue.popleft()

            # If the location is already visited or exceeds cost, skip it
            if (r, c) in visited or cost > self.prosperity or sea_map[r][c]:
                continue

            visited.add((r, c))
            self.territory.append((r, c))  # Add the valid cell to the city's territory

            # Explore neighboring cells (Up, Down, Left, Right)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1,-1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:  # Stay within bounds
                    next_cost = cost + (traversal_cost_map[nr, nc] * 2)
                    queue.append((nr, nc, next_cost)) 