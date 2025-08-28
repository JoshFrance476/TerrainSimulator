import numpy as np
from utils.config import WORLD_ROWS, WORLD_COLS
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement


def generate_stage_6(cities_list, traversal_cost_map, colour_map):
    traversal_cost_multiplier_map = np.ones((WORLD_ROWS, WORLD_COLS), dtype=float)

    for city in cities_list:
        path = find_path(city, (100,100), traversal_cost_map) #'path' is an array of x, y coords
        for x, y in path:
            traversal_cost_multiplier_map[y][x] -= 0.05

    colour_map_with_paths = path_lightening(traversal_cost_multiplier_map, colour_map)
    return traversal_cost_multiplier_map, colour_map_with_paths

def find_path(start, end, traversal_cost_map):
    grid = Grid(matrix=traversal_cost_map)

    start_grid = grid.node(start[1], start[0])
    end_grid = grid.node(end[1], end[0])  

    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

    path, runs = finder.find_path(start_grid, end_grid, grid)

    return path

def path_lightening(traversal_cost_multiplier_map, colour_map):
    # Calculate lightening factor (values below 1)
    lightening_factor = 1 - traversal_cost_multiplier_map  # Values closer to 1 will lighten less

    # Blend colors with white based on lightening factor
    colour_map = colour_map + ((255-colour_map) * lightening_factor[:, :, None]).astype(np.uint8)

    return colour_map