import pygame
import sys
import config
from stage_1_generator import generate_stage_1
from stage_2_generator import generate_stage_2
from stage_3_generator import generate_stage_3
from stage_4_generator import generate_stage_4
from stage_5_generator import generate_stage_5
from stage_6_generator import generate_stage_6
import numpy as np 
import time
import logging

logging.basicConfig(level=logging.DEBUG)

font_path = "fonts\OldNewspaperTypes.ttf"

# Initialize Pygame
pygame.init()
font = pygame.font.Font(font_path, 24)
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("Terrain Generation")

def draw_terrain(display_map, screen):
    """
    Draw the terrain grid with the selected filter applied.
    
    Args:
        terrain (list): The terrain grid.
        current_filter (str): The type of filter to apply when displaying.
    """
    for r in range(config.ROWS):
        for c in range(config.COLS):
            colour = display_map[r][c]
            pygame.draw.rect(screen, colour, (c * config.CELL_SIZE, r * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE))
    pygame.display.flip()


def label_cities(city_map, city_names, cell_size):
    city_count = 0
    for row in range(city_map.shape[0]):
        for col in range(city_map.shape[1]):
            if city_map[row][col]:  # If city exists at this location
                city_name = city_names[city_count % len(city_names)]
                city_count += 1

                # Render city name text
                text_surface = font.render(city_name, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(
                    (col * cell_size + cell_size // 2) + 30,
                    (row * cell_size + cell_size // 2) + 18
                ))

                screen.blit(text_surface, text_rect)



def draw_text_with_outline(screen, text, font, position, base_color, outline_color, outline_thickness=0.0):
    """
    Draw text with an outline effect.

    Args:
        screen (pygame.Surface): The screen to render the text on.
        text (str): The text to render.
        font (pygame.font.Font): Pygame font object.
        position (tuple): (x, y) position of the text.
        base_color (tuple): RGB color of the main text.
        outline_color (tuple): RGB color of the outline.
        outline_thickness (int): Thickness of the outline effect.
    """
    x, y = position
    x+=5
    y+=5

    # Render the outline by drawing multiple copies of the text
    for dx in [-outline_thickness, 0, outline_thickness]:
        for dy in [-outline_thickness, 0, outline_thickness]:
            if dx != 0 or dy != 0:  # Avoid center overlap
                outline_surface = font.render(text, True, outline_color)
                screen.blit(outline_surface, (x + dx, y + dy))

    # Render the main text (base color)
    text_surface = font.render(text, True, base_color)
    screen.blit(text_surface, (x, y))


def main():
    """
    Main function to run the terrain visualization.
    """
    start_time = time.time()
    elevation_map, rainfall_map, temperature_map = generate_stage_1(config.ROWS, config.COLS, config.SCALE, config.SEED)
    logging.debug(f"Stage 1 generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    river_map, sea_map, steepness_map = generate_stage_2(config.ROWS, config.COLS, config.NUMBER_OF_RIVERS, config.SEA_LEVEL, elevation_map, config.RIVER_SOURCE_MIN_ELEVATION)
    logging.debug(f"Stage 2 generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map, colour_map, desiribility_map = generate_stage_3(config.ROWS, config.COLS, river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map, config.REGION_CONDITIONS, config.REGION_COLORS, config.REGIONS_TO_BLEND)
    logging.debug(f"Stage 3 generation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    population_map = generate_stage_4(desiribility_map)
    logging.debug(f"Stage 4 generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    cities_map, cities_list = generate_stage_5(population_map, config.NUMBER_OF_CITIES)
    logging.debug(f"Stage 5 generation took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    traversal_cost_multiplier_map, colour_map_with_paths = generate_stage_6(cities_list, traversal_cost_map, colour_map)
    logging.debug(f"Stage 6 generation took {time.time() - start_time:.2f} seconds")

    colour_map_with_paths[cities_map] = (0,0,0)

    display_map = colour_map_with_paths

    clock = pygame.time.Clock()

    city_names = [f"City {i+1}" for i in range(config.NUMBER_OF_CITIES)]

    needs_update = True

    show_city_labels = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    show_city_labels = not show_city_labels
                needs_update = True

        if needs_update:
            screen.fill((0, 0, 0))  # Clear screen only when necessary
            draw_terrain(display_map, screen)
            if show_city_labels:
                label_cities(cities_map, city_names, config.CELL_SIZE)
            pygame.display.flip()
            needs_update = False  # Reset update flag

        clock.tick(2)


if __name__ == "__main__":
    main()
