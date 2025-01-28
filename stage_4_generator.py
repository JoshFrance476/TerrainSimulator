import numpy as np

def generate_stage_4(desiribility_map):
    population_map = set_populations(desiribility_map)
    return population_map


def set_populations(desiribility_map):
    rows, cols = len(desiribility_map), len(desiribility_map[0])
    population_map = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            population_map[r][c] = desiribility_map[r][c]
    
    return population_map
