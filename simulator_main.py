import numpy as np
import config
from generator_main import generate_initial_maps
from overlay_generator import apply_heatmap_overlay, generate_coastline_map, generate_territory_overlay
from find_top_desiribility import find_top_desiribility_points
from AnchorPoint import AnchorPoint
import random


def simulate_init():
    global desiribility_map, desiribility_display, colour_display, population_display, outline_display, steepness_display, elevation_display, traversal_cost_map, sea_map, river_map, territory_display, cities_list, population_map
    colour_display, desiribility_map, elevation_map, traversal_cost_map, sea_map, river_map, steepness_map = generate_initial_maps()
    outline_display = generate_coastline_map(elevation_map)
    population_map = np.zeros((config.ROWS, config.COLS), dtype=float)
    population_map = update_population(population_map)

    AnchorPoint.initialise(traversal_cost_map, sea_map, river_map)
    
    initialise_cities(population_map)

    territory_display = generate_territory_overlay(colour_display, AnchorPoint.get_uid_map(), AnchorPoint.get_anchors())
    elevation_display = apply_heatmap_overlay(elevation_map, outline_display)
    population_display = apply_heatmap_overlay(population_map, outline_display, "inferno")
    desiribility_display = apply_heatmap_overlay(desiribility_map, outline_display, "inferno")
    steepness_display = apply_heatmap_overlay(steepness_map, outline_display, "inferno")

    terrain_data = {
        "elevation": elevation_map,
        "desirability": desiribility_map,
        "population": population_map,
        "steepness": steepness_map,
        "traversal cost": traversal_cost_map
    }

    return terrain_data

    
 

def simulate_loop(filter):
    global population_display, desiribility_display, elevation_display, traversal_cost_map, territory_display, population_map
    population_map = update_population(population_map)
    mod_filter = filter % 5

    if mod_filter == 0:
        display_map = colour_display
    elif mod_filter == 1:
        display_map = desiribility_display
    elif mod_filter == 2:
        display_map = steepness_display
    elif mod_filter == 3:
        population_display = apply_heatmap_overlay(population_map, outline_display, "inferno")
        display_map = population_display
    elif mod_filter == 4:
        for anchor in AnchorPoint.get_anchors():
            anchor.update_territory_size()
        AnchorPoint.generate_territory_uid_map()
        display_map = generate_territory_overlay(colour_display, AnchorPoint.get_uid_map(), AnchorPoint.get_anchors())

    return display_map


def update_population(population_map):
    # Create a boolean mask where desiribility_map above threshold
    mask = desiribility_map > 0.5  

    # Apply the population growth formula only where the condition is True
    population_map[mask] += desiribility_map[mask] / 10

    # limits populations to 10
    population_map[mask] = np.minimum(10, population_map[mask] + desiribility_map[mask] / 10)
    

    return population_map


#Returns list of anchor objects located at the top n desiribility points
def initialise_cities(population_map):

    # Find anchor locations
    anchor_location_list = find_top_desiribility_points(population_map, config.NUMBER_OF_CITIES, config.CITIES_MIN_DISTANCE)

    for uid, (_, (r, c)) in enumerate(anchor_location_list):
        AnchorPoint((r, c), uid+1)
    
    AnchorPoint.generate_territory_uid_map()
        



    


