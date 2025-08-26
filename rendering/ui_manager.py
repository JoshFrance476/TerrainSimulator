import pygame
from utils import config

class UIManager:
    def __init__(self):
        self.font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)

    def draw_sidebar(self, selected_cell, screen, static_maps, dynamic_maps):
        """ Draws a sidebar with information about the selected cell. """
        sidebar_x = config.WIDTH
        
        # Draw sidebar background
        pygame.draw.rect(screen, (220, 220, 220), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.HEIGHT))  

        # Draw sidebar border (Black, 3px thickness)
        pygame.draw.rect(screen, (80, 80, 80), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.HEIGHT), 3)


        # Display title
        title_text = self.font.render("Cell Info", True, (30, 30, 30))
        screen.blit(title_text, (sidebar_x + 10, 20))


        if selected_cell:
            r, c = selected_cell  # Selected cell coordinates
            

            # Fetch data from terrain maps
            region = static_maps["region_map"][r, c]
            elevation = static_maps["elevation_map"][r, c]
            desirability = static_maps["desiribility_map"][r, c]
            steepness = static_maps["steepness_map"][r, c]
            traversal_cost = static_maps["traversal_cost_map"][r, c]
            population = dynamic_maps["population_map"][r, c]


            # List of text entries to display
            info_lines = [
                f"Row: {r}, Col: {c}",
                f"Region: {region.title()}", # First letter of each word is capital
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
    

 


    def draw_hover_highlight(self, hovered_cell, screen, x_offset, y_offset, zoom_level, color=(255, 255, 255, 100)):
        """Draws a semi-transparent highlight over the hovered cell."""
        cell_y, cell_x = hovered_cell  # Ensure correct row/col order

        # Compute cell size after zooming
        scaled_cell_size = config.CELL_SIZE * zoom_level


        # Convert grid cell to screen coordinates (adjust for zoom & panning)
        screen_x = (cell_x * scaled_cell_size) - x_offset
        screen_y = (cell_y * scaled_cell_size) - y_offset

        # Ensure highlight surface has transparency
        highlight_surface = pygame.Surface((scaled_cell_size, scaled_cell_size), pygame.SRCALPHA)
        highlight_surface.fill(color)

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))


    def draw_selected_cell_border(self, selected_cell, screen, x_offset, y_offset, zoom_level, cell_size, color=(255, 255, 0)):
        """Draws a border around the selected cell."""
        cell_y, cell_x = selected_cell  # Ensure correct row/col order


        # Compute cell size after zooming
        scaled_cell_size = cell_size * zoom_level

        # Convert grid cell to screen coordinates (adjust for zoom & panning)
        screen_x = (cell_x * scaled_cell_size) - x_offset
        screen_y = (cell_y * scaled_cell_size) - y_offset

        # Create transparent surface for the border
        highlight_surface = pygame.Surface((scaled_cell_size, scaled_cell_size), pygame.SRCALPHA)
        
        # Scale border thickness with cell size for consistent appearance
        min_thickness = 1
        max_thickness = 4
        thickness_ratio = 0.1  # Thickness as a proportion of cell size
        scaled_thickness = max(min_thickness, min(max_thickness, int(scaled_cell_size * thickness_ratio)))
        
        # Draw rectangle border with scaled thickness
        pygame.draw.rect(
            highlight_surface,
            color,
            (0, 0, scaled_cell_size, scaled_cell_size),
            scaled_thickness
        )

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))






