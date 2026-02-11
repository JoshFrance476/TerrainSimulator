import numpy as np
from config import RESOURCE_LOOKUP, RESOURCE_RULES, BIOME_NAME_TO_ID

def calculate_population_capacity_map(fertility, temperature, proximity_to_water, sea, river, water_threshold=5):
    # mask of cells that are sea or river
    water_mask = sea | river

    # temp_factor = 1 - abs(0.4 - temperature)
    temp_factor = 1 - np.abs(0.4 - temperature)

    # water_bonus = max(0, (water_threshold - proximity) / water_threshold * 0.3)
    water_bonus = (water_threshold - proximity_to_water) / water_threshold * 0.3
    water_bonus = np.maximum(water_bonus, 0)

    # base capacity
    capacity = (fertility * 2) * temp_factor + water_bonus

    # multiply by random field
    rand = np.random.power(1, size=capacity.shape)
    capacity *= rand

    # zero out water + river
    capacity[water_mask] = 0

    return capacity.astype(np.float32)



def calculate_resource_map(fertility_map, temperature_map, elevation_map, biome_map, rainfall_map):
    # Thank you ChatGPT. Applies all rules set out in RESOURCE_RULES to generate resource map
    rows, cols = fertility_map.shape
    probability_stack = np.zeros((rows, cols, len(RESOURCE_LOOKUP)))

    for resource, rules in RESOURCE_RULES.items():
        resource_id = RESOURCE_LOOKUP[resource]
        probability_map = np.zeros((rows, cols), dtype=np.float32)

        if "biome" in rules:
            for biome_name, weight in rules["biome"].items():
                probability_map[biome_map == BIOME_NAME_TO_ID[biome_name]] += weight

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
