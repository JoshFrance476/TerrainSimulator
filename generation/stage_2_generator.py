import random
import numpy as np
import utils.config as config
from scipy.ndimage import binary_dilation

def generate_stage_2(rows, cols, number_of_rivers, sea_level, elevation_map, river_source_min_elevation):
    # Initialize an empty river map
    sea_map = np.zeros((rows, cols), dtype=bool)
    river_map = np.zeros((rows, cols), dtype=bool)
    steepness_map = np.zeros((rows, cols), dtype=float)

    for _ in range(number_of_rivers):
        single_river_map = generate_river_map(elevation_map, sea_level, river_source_min_elevation)
        river_map = np.logical_or(river_map, single_river_map)

    for r in range(rows):
        for c in range(cols):
            if elevation_map[r][c] < sea_level:
                sea_map[r][c] = True
            steepness_map[r][c] = calculate_steepness(elevation_map, r, c)
    
    coastline_map = generate_coastline_map(elevation_map)
    
    return river_map, sea_map, steepness_map, coastline_map
            


def generate_river_map(elevation_map, sea_level, river_source_min_elevation):
    """
    Generate a river by finding a random land cell and flowing to the sea.
    If no downhill movement is possible, the river flows to the next lowest neighbor.

    Args:
        elevation_map (list): 2D elevation data.

    Returns:
        list: 2D boolean map where True represents river cells.
    """
    rows, cols = len(elevation_map), len(elevation_map[0])


    river_map = np.zeros((rows, cols), dtype=bool)

    # Find a random land cell (elevation > 0)
    while True:
        start_row = random.randint(0, rows - 1)
        start_col = random.randint(0, cols - 1)
        if elevation_map[start_row][start_col] > river_source_min_elevation:  # Ensure starting on land
            break

    current_row, current_col = start_row, start_col

    while elevation_map[current_row][current_col] > sea_level:
        river_map[current_row][current_col] = True  # Mark as river

        next_row, next_col = find_lowest_neighbour(elevation_map, river_map, current_row, current_col)

        if current_col == next_col and current_row == next_row:
            break
        else:
            current_row, current_col = next_row, next_col

    return river_map


def find_lowest_neighbour(elevation_map, river_map, row, col):
    rows, cols = len(elevation_map), len(elevation_map[0])

    # Define 8 possible movement directions (N, S, E, W, and diagonals)
    directions = [
        (-1, 0),  # North
        (1, 0),   # South
        (0, -1),  # West
        (0, 1),   # East

    ]

    # Initialize variables with the current position as a fallback
    lowest_elevation = elevation_map[row][col]  
    lowest_pos = (row, col)

    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            # Always consider unvisited cells, even if they are higher
            if not river_map[nr][nc]:  
                if elevation_map[nr][nc] < lowest_elevation or lowest_pos == (row, col):
                    lowest_elevation = elevation_map[nr][nc]
                    lowest_pos = (nr, nc)
    return lowest_pos


def calculate_steepness(elevation_map, row, col):
    """
    Calculate terrain steepness based on elevation difference between opposite neighbors, normalized to [0, 1].
    """
    rows, cols = len(elevation_map), len(elevation_map[0])


    def get_elevation(r, c):
        if 0 <= r < rows and 0 <= c < cols:
            return elevation_map[r][c]
        return 0  # Default for out-of-bounds

    north_south = abs(get_elevation(row - 1, col) - get_elevation(row + 1, col))
    east_west = abs(get_elevation(row, col - 1) - get_elevation(row, col + 1))
    steepness = max(north_south, east_west)  # Max difference between opposite neighbors

    return normalize(steepness, 0, 1)

def generate_coastline_map(elevation_map):
        rows, cols, = elevation_map.shape

        coastline_map = np.zeros((rows, cols), dtype=np.uint8)  # White background

        land_mask = elevation_map > config.SEA_LEVEL
        sea_mask = elevation_map <= config.SEA_LEVEL

        # coastline = land cells that touch sea OR sea cells that touch land
        
        coastline_mask = land_mask & binary_dilation(sea_mask)

        coastline_map[coastline_mask] = 1

        return coastline_map


def normalize(value, min_value, max_value):
    """
    Normalize a value to the range [0, 1].
    """
    return (value - min_value) / (max_value - min_value)


