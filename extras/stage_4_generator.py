import numpy as np

def generate_stage_4(desiribility_map):
    population_map = np.zeros_like(desiribility_map)
    population_map = update_population(desiribility_map, population_map)
    return population_map


def update_population(desiribility_map, population_map):
    # Create a boolean mask where desiribility_map above threshold
    mask = desiribility_map > 0.5  


    # limits populations to 10
    population_map[mask] = np.minimum(10, population_map[mask] + desiribility_map[mask] / 500)
    

    return population_map