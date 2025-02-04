import numpy as np
import config
from generator_main import generate_initial_maps
from overlay_generator import apply_heatmap_overlay, generate_coastline_map
from find_top_desiribility import find_top_desiribility_points
from City import City
import random


def simulate_init():
    global desiribility_map, desiribility_display, colour_display, population_display, outline_display, elevation_display, traversal_cost_map, sea_map, territory_map, population_map
    colour_display, desiribility_map, elevation_map, traversal_cost_map, sea_map = generate_initial_maps()
    outline_display = generate_coastline_map(elevation_map)
    population_map = np.zeros((config.ROWS, config.COLS), dtype=float)
    population_map = update_population(population_map)
    display_map, cities_list = generate_cities(population_map, colour_display)


    territory_map = generate_territory_map(display_map, cities_list)
    elevation_display = apply_heatmap_overlay(elevation_map, outline_display)
    population_display = apply_heatmap_overlay(population_map, outline_display, "inferno")
    desiribility_display = apply_heatmap_overlay(desiribility_map, outline_display, "inferno")

    
 

def simulate_loop(filter):
    global population_display, desiribility_display, elevation_display, traversal_cost_map, territory_map, population_map
    population_map = update_population(population_map)
    mod_filter = filter % 5

    if mod_filter == 0:
        display_map = colour_display
    elif mod_filter == 1:
        display_map = elevation_display
    elif mod_filter == 2:
        display_map = population_display
    elif mod_filter == 3:
        display_map = desiribility_display
    elif mod_filter == 4:
        display_map = territory_map
    

    return display_map


def update_population(population_map):
    # Create a boolean mask where desiribility_map above threshold
    mask = desiribility_map > 0.5  

    # Apply the population growth formula only where the condition is True
    population_map[mask] += desiribility_map[mask] / 10

    return population_map


def generate_cities(population_map, colour_display):
    cities_map = colour_display.copy()
    cities_list = []  # Initialize a list to store City objects

    # Find city locations
    cities_location_list = find_top_desiribility_points(population_map, config.NUMBER_OF_CITIES, config.CITIES_MIN_DISTANCE)

    # Apply black mask to each city location and store City objects
    for _, (r, c) in cities_location_list:
        cities_map[r, c] = [0, 0, 0]  # Set pixel to black
        cities_list.append(City((r, c),random.randint(*config.CITY_PROSPERITY_RANGE)))  # Store City object in the list

    return cities_map, cities_list  # Return updated map and list of City objects

def generate_territory_map(display_map, cities_list):
    territory_map = display_map.copy()
    for city in cities_list:
        city.generate_territory(traversal_cost_map, sea_map)
        city_colour = city.get_colour()
        for (r, c) in city.get_territory():
            territory_map[r, c] = city_colour  # Set the city's color in its territory
            if (r, c) == city.get_location():
                territory_map[r, c] = [0,0,0]
    return territory_map
    


