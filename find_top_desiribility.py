import numpy as np

def find_top_desiribility_points(desiribility_map, N=3, min_distance=5):
    """
    Finds the top N highest population values ensuring they are at least `min_distance` cells apart.

    Args:
        population_map (numpy array): 2D array containing population density values.
        N (int): Number of top locations to find.
        min_distance (int): Minimum required distance (Manhattan distance) between selected locations.

    Returns:
        list: List of tuples (population_value, (row, col)) representing the highest values and their locations.
    """
    selected_points = []
    population_map_copy = desiribility_map.copy()  # Work on a copy to avoid modifying the original data

    for _ in range(N):
        # Find the maximum value and its location
        max_index = np.argmax(population_map_copy)
        max_value = population_map_copy.flat[max_index]  # Get max value
        max_location = np.unravel_index(max_index, population_map_copy.shape)

        # Store result
        selected_points.append((max_value, max_location))

        # Mask out nearby cells within `min_distance`
        r, c = max_location
        row_start, row_end = max(0, r - min_distance), min(desiribility_map.shape[0], r + min_distance + 1)
        col_start, col_end = max(0, c - min_distance), min(desiribility_map.shape[1], c + min_distance + 1)

        # Set the masked area to a very low value so it won't be picked again
        population_map_copy[row_start:row_end, col_start:col_end] = -np.inf

    return selected_points
