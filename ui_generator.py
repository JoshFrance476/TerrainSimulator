import pygame
import utils.config as config



def draw_sidebar(screen, selected_cell, terrain_data):
    """ Draws a sidebar with information about the selected cell. """
    sidebar_x = config.WIDTH
    
    # Draw sidebar background
    pygame.draw.rect(screen, (220, 220, 220), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.HEIGHT))  

    # Draw sidebar border (Black, 3px thickness)
    pygame.draw.rect(screen, (80, 80, 80), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.HEIGHT), 3)

    font = pygame.font.Font("fonts\VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)

    # Display title
    title_text = font.render("Cell Info", True, (30, 30, 30))
    screen.blit(title_text, (sidebar_x + 10, 20))

    if selected_cell:
        r, c = selected_cell  # Selected cell coordinates
        
        # Fetch data from terrain maps
        elevation = terrain_data["elevation"][r, c]
        desirability = terrain_data["desirability"][r, c]
        population = terrain_data["population"][r, c]
        steepness = terrain_data["steepness"][r, c]
        traversal_cost = terrain_data["traversal cost"][r, c]

        # List of text entries to display
        info_lines = [
            f"Row: {r}, Col: {c}",
            f"Elevation: {elevation:.2f}",
            f"Desirability: {desirability:.2f}",
            f"Population: {population:.2f}",
            f"steepness: {steepness:.2f}",
            f"traversal cost: {traversal_cost:.2f}",
        ]

        # Render and display each line
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, (30, 30, 30))
            screen.blit(text_surface, (sidebar_x + 10, 50 + i * 25))
