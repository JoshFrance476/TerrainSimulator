import numpy as np

def generate_stage_4(rows, cols, static_data):
    population_capacity_map = np.zeros((rows, cols), dtype=np.float32)
    population_map = np.zeros((rows, cols), dtype=np.float32)

    fertility_map = static_data["fertility"]
    temperature_map = static_data["temperature"]
    river_proximity_map = static_data["river_proximity"]
    sea_map = static_data["sea"]
    river_map = static_data["river"]
    elevation_map = static_data["elevation"]

    population_capacity_map = np.vectorize(calculate_population_capacity, otypes=[np.float32])(fertility_map, temperature_map, river_proximity_map, sea_map, river_map, elevation_map)


    return population_capacity_map, population_map



def calculate_population_capacity(fertility, temperature, proximity_to_water, sea, river, elevation, water_threshold=5):
    """
    Calculates population capacity based on fertility, temperature, and proximity to water. Can use Numpy vectorization instead in future.
    """
    if sea or river:
        return 0 
    
    capacity = 1

    temp_factor = 1 - abs(0.5 - temperature)  # Best temperature around 0.5
    water_bonus = max(0, (water_threshold - proximity_to_water) / water_threshold * 0.3)

    capacity += fertility * temp_factor + water_bonus
    
    return capacity
