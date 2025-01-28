import numpy as np

def generate_stage_5(population_map, number_of_cities):
    cities_map, cities_list = set_cities(population_map, number_of_cities, 32)
    return cities_map, cities_list


def set_cities(population_map, n_cities, min_distance):
    cities_list = []
    rows, cols = len(population_map), len(population_map[0])
    cities_map = np.zeros((rows, cols), dtype=bool)

    flattened_population = np.array(population_map).flatten()
    sorted_indices = np.argsort(flattened_population)[::-1]  # Sort in descending order

    selected_cities = []

    for index in sorted_indices:  # Iterate over sorted indices
        if len(selected_cities) >= n_cities:  # Stop once the required number of cities is placed
            break

        row, col = divmod(index, cols)
        
        # Check minimum distance constraint
        if all(np.sqrt((row - r)**2 + (col - c)**2) >= min_distance for r, c in selected_cities):
            selected_cities.append((row, col))
            cities_map[row][col] = True
            cities_list.append((row, col))
            #print(f"City placed at: ({row}, {col})")

    return cities_map, cities_list
