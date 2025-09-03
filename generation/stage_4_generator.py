import numpy as np
from utils.config import RESOURCE_LOOKUP, RESOURCE_RULES, REGION_LOOKUP


def generate_stage_4(static_data):
    fertility_map = static_data["fertility"]
    temperature_map = static_data["temperature"]
    river_proximity_map = static_data["river_proximity"]
    sea_map = static_data["sea"]
    river_map = static_data["river"]
    elevation_map = static_data["elevation"]

    population_capacity_map = np.vectorize(calculate_population_capacity, otypes=[np.float32])(fertility_map, temperature_map, river_proximity_map, sea_map, river_map, elevation_map)

    population_map = init_population(population_capacity_map)

    resource_map = calculate_resource_map(static_data)


    return population_capacity_map, population_map, resource_map



def calculate_population_capacity(fertility, temperature, proximity_to_water, sea, river, elevation, water_threshold=5):
    """
    Calculates population capacity based on fertility, temperature, and proximity to water. Can use Numpy vectorization instead in future.
    """
    if sea or river:
        return 0 
    
    capacity = 0

    temp_factor = 1 - abs(0.4 - temperature)  # Best temperature around 0.5
    water_bonus = max(0, (water_threshold - proximity_to_water) / water_threshold * 0.3)

    capacity += (fertility*2) * temp_factor + water_bonus 

    #Multiplies by random float between 0 and 1
    capacity *= np.random.power(1)
    
    return capacity


def calculate_resource_map(static_data):
    # Thank you ChatGPT. Applies all rules set out in RESOURCE_RULES to generate resource map
    rows, cols = static_data["elevation"].shape
    probability_stack = np.zeros((rows, cols, len(RESOURCE_LOOKUP)))

    for resource, rules in RESOURCE_RULES.items():
        resource_id = RESOURCE_LOOKUP[resource]
        probability_map = np.zeros((rows, cols), dtype=np.float32)

        if "region" in rules:
            for region_name, weight in rules["region"].items():
                probability_map[static_data["region"] == REGION_LOOKUP[region_name]] += weight

        if "fertility" in rules:
            probability_map *= 1 / (1 + np.exp(-rules["fertility"] * (static_data["fertility"] - 0.5)))

        if "rainfall" in rules:
            probability_map *= 1 / (1 + np.exp(-rules["rainfall"] * (static_data["rainfall"] - 0.5)))
        
        if "temperature" in rules:
            probability_map *= 1 / (1 + np.exp(-rules["temperature"] * (static_data["temperature"] - 0.5)))
        
        if "elevation" in rules:
            probability_map *= 1 / (1 + np.exp(-rules["elevation"] * (static_data["elevation"] - 0.5)))

        
        
        probability_stack[:, :, resource_id] = probability_map

    probability_stack[:, :, RESOURCE_LOOKUP["none"]] = 0.8
        
    probability_stack /= probability_stack.sum(axis=-1, keepdims=True)

    flat_probability_stack = probability_stack.reshape(-1, len(RESOURCE_LOOKUP))

    gumbel_noise = -np.log(-np.log(np.random.rand(*flat_probability_stack.shape)))
    samples = np.argmax(np.log(flat_probability_stack + 1e-12) + gumbel_noise, axis=1)
    resource_map = samples.reshape(rows, cols).astype(np.int8)


    return resource_map

def init_population(population_capacity_map):
        population_map = population_capacity_map.copy()

        return population_map
