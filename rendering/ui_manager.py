import pygame
from utils import config

class UIManager:
    def __init__(self):
        self.font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)

    def draw_sidebar(self, selected_cell, screen, world_data, dynamic_maps):
        """ Draws a sidebar with information about the selected cell. """
        sidebar_x = config.SCREEN_WIDTH
        
        # Draw sidebar background
        pygame.draw.rect(screen, (220, 220, 220), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))  

        # Draw sidebar border (Black, 3px thickness)
        pygame.draw.rect(screen, (80, 80, 80), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)


        # Display title
        title_text = self.font.render("Cell Info", True, (30, 30, 30))
        screen.blit(title_text, (sidebar_x + 10, 20))


        if selected_cell:
            r, c = selected_cell  # Selected cell coordinates
            

            # Fetch data from terrain maps
            region = world_data["region"][r, c]
            elevation = world_data["elevation"][r, c]
            desirability = world_data["desiribility"][r, c]
            steepness = world_data["steepness"][r, c]
            traversal_cost = world_data["traversal_cost"][r, c]
            population = dynamic_maps["population_map"][r, c]


            # List of text entries to display
            info_lines = [
                f"Row: {r}, Col: {c}",
                f"Region: {region}", # First letter of each word is capital
                f"Elevation: {elevation:.2f}",
                f"Desirability: {desirability:.2f}",
                f"steepness: {steepness:.2f}",
                f"traversal cost: {traversal_cost:.2f}",
                f"population: {population:.2f}",
            ]


            # Render and display each line
            for i, line in enumerate(info_lines):
                text_surface = self.font.render(line, True, (30, 30, 30))
                screen.blit(text_surface, (sidebar_x + 10, 50 + i * 25))
    

 


    def draw_hover_highlight(self, hovered_cell, screen, camera_x_pos, camera_y_pos, color=(255, 255, 255, 100)):
        """Draws a semi-transparent highlight over the hovered cell."""
        cell_y, cell_x = hovered_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - camera_x_pos) * config.CELL_SIZE
        screen_y = (cell_y - camera_y_pos) * config.CELL_SIZE

        # Create transparent surface for the highlight
        highlight_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(color)

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))


    def draw_selected_cell_border(self, selected_cell, screen, camera_x_pos, camera_y_pos, cell_size, color=(255, 255, 0)):
        """Draws a border around the selected cell."""
        cell_y, cell_x = selected_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - camera_x_pos) * config.CELL_SIZE
        screen_y = (cell_y - camera_y_pos) * config.CELL_SIZE

        # Create transparent surface for the border
        highlight_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        
        
        # Draw rectangle border with scaled thickness
        pygame.draw.rect(
            highlight_surface,
            color,
            (0, 0, config.CELL_SIZE, config.CELL_SIZE),
            1
        )

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))






