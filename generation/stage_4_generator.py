import numpy as np
from utils.config import RESOURCE_LOOKUP, RESOURCE_RULES, REGION_LOOKUP


def generate_stage_4(fertility_map, temperature_map, river_proximity_map, sea_map, river_map, elevation_map, region_map, rainfall_map):


    population_capacity_map = np.vectorize(calculate_population_capacity, otypes=[np.float32])(fertility_map, temperature_map, river_proximity_map, sea_map, river_map)

    population_map = init_population(population_capacity_map)

    resource_map = calculate_resource_map(fertility_map, temperature_map, elevation_map, region_map, rainfall_map)


    return population_capacity_map, population_map, resource_map



def calculate_population_capacity(fertility, temperature, proximity_to_water, sea, river, water_threshold=5):
    """
    Calculates population capacity based on fertility, temperature, and proximity to water. Can use Numpy vectorization instead in future.
    """
    if sea or river:
        return 0 
    
    capacity = 0

    temp_factor = 1 - abs(0.4 - temperature)  # Best temperature around 0.4
    water_bonus = max(0, (water_threshold - proximity_to_water) / water_threshold * 0.3)

    capacity += (fertility*2) * temp_factor + water_bonus 

    #Multiplies by random float between 0 and 1
    capacity *= np.random.power(1)
    
    return capacity


def calculate_resource_map(fertility_map, temperature_map, elevation_map, region_map, rainfall_map):
    # Thank you ChatGPT. Applies all rules set out in RESOURCE_RULES to generate resource map
    rows, cols = fertility_map.shape
    probability_stack = np.zeros((rows, cols, len(RESOURCE_LOOKUP)))

    for resource, rules in RESOURCE_RULES.items():
        resource_id = RESOURCE_LOOKUP[resource]
        probability_map = np.zeros((rows, cols), dtype=np.float32)

        if "region" in rules:
            for region_name, weight in rules["region"].items():
                probability_map[region_map == REGION_LOOKUP[region_name]] += weight

        if "fertility" in rules:
            probability_map *= factor_from_range(fertility_map, rules["fertility"])

        if "rainfall" in rules:
            probability_map *= factor_from_range(rainfall_map, rules["rainfall"])
        
        if "temperature" in rules:
            probability_map *= factor_from_range(temperature_map, rules["temperature"])
        
        if "elevation" in rules:
            probability_map *= factor_from_range(elevation_map, rules["elevation"])

        
        
        probability_stack[:, :, resource_id] = probability_map

    probability_stack[:, :, RESOURCE_LOOKUP["none"]] = 0.8
        
    probability_stack /= probability_stack.sum(axis=-1, keepdims=True)

    flat_probability_stack = probability_stack.reshape(-1, len(RESOURCE_LOOKUP))

    gumbel_noise = -np.log(-np.log(np.random.rand(*flat_probability_stack.shape)))
    samples = np.argmax(np.log(flat_probability_stack + 1e-12) + gumbel_noise, axis=1)
    resource_map = samples.reshape(rows, cols).astype(np.int8)


    return resource_map

def factor_from_range(values, rule):
    vmin, vmax, weight = rule["min"], rule["max"], rule["weight"]

    mask = (values >= vmin) & (values <= vmax)
    out = np.zeros_like(values, dtype=np.float32)

    denom = max(vmax - vmin, 1e-9)
    norm = (values - vmin) / denom 
    norm = np.clip(norm, 0.0, 1.0)

    if weight == 0:
        out[mask] = 1.0
    elif weight > 0:
        out[mask] = norm[mask] ** weight
    else:
        out[mask] = (1 - norm[mask]) ** abs(weight)

    return out


def init_population(population_capacity_map):
        population_map = population_capacity_map.copy()

        return population_map
