import pygame
import config

# Sidebar dimensions
SIDEBAR_WIDTH = 250  
FONT_SIZE = 20

def draw_sidebar(screen, selected_cell, terrain_data):
    """ Draws a sidebar with information about the selected cell. """
    sidebar_x = config.WIDTH - SIDEBAR_WIDTH
    pygame.draw.rect(screen, (40, 40, 40), (sidebar_x, 0, SIDEBAR_WIDTH, config.HEIGHT))  # Sidebar background

    font = pygame.font.Font(None, FONT_SIZE)
    
    # Display title
    title_text = font.render("Cell Info", True, (255, 255, 255))
    screen.blit(title_text, (sidebar_x + 10, 20))

    #for city in city_list

    if selected_cell:
        r, c = selected_cell  # Selected cell coordinates
        
        # Fetch data from terrain maps
        elevation = terrain_data["elevation"][r, c]
        desirability = terrain_data["desirability"][r, c]
        population = terrain_data["population"][r, c]

        # List of text entries to display
        info_lines = [
            f"Row: {r}, Col: {c}",
            f"Elevation: {elevation:.2f}",
            f"Desirability: {desirability:.2f}",
            f"Population: {population:.2f}",
        ]

        # Render and display each line
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (sidebar_x + 10, 50 + i * 25))