import pygame
from utils import config

class UIManager:
    def __init__(self):
        self.large_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)
        self.small_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE-3)
    
    def render_ui(self, screen, cell_data, settlements_dict, camera_x, camera_y, filter, relevant_cells):
        cell_data, settlement_data = cell_data
        selected_cell, hovered_cell = relevant_cells
        self.draw_settlements(settlements_dict, screen, camera_x, camera_y)
        self.draw_left_sidebar(screen, settlements_dict)
        self.draw_right_sidebar(screen, cell_data, settlement_data, selected_cell, filter)
        self.draw_hover_highlight(hovered_cell, screen, camera_x, camera_y)

        if selected_cell:
            self.draw_selected_cell_border(selected_cell, screen, camera_x, camera_y)


    def draw_settlements(self, settlements_dict, screen, camera_x, camera_y):
        for s in settlements_dict.values():
            x = (s.c - camera_x) * config.CELL_SIZE + config.SIDEBAR_WIDTH
            y = (s.r - camera_y) * config.CELL_SIZE
            pygame.draw.rect(screen, (0, 0, 0), (x, y, config.CELL_SIZE, config.CELL_SIZE))
            text_surface = self.large_font.render(s.name, True, (30, 30, 30))
            screen.blit(text_surface, (x + 5, y - 5))


    def draw_left_sidebar(self, screen, settlements_dict):


        pygame.draw.rect(screen, (220, 220, 220), (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80, 80, 80), (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        title_text = self.large_font.render("Settlements List", True, (30, 30, 30))
        screen.blit(title_text, (10, 20))


        for idx, s in enumerate(settlements_dict.values()):
            settlement_name = s.name
            settlement_r = s.r
            settlement_c = s.c
            settlement_population = s.population


            info_lines = [
                f"Name: {settlement_name}",
                f"Row: {settlement_r}, Col: {settlement_c}",
                f"Population: {settlement_population:.2f}"
            ]

            text_surface = self.large_font.render(info_lines[0], True, (30, 30, 30))
            screen.blit(text_surface, (10, 50 + (idx * 60)))

            text_surface = self.small_font.render(info_lines[1], True, (30, 30, 30))
            screen.blit(text_surface, (10, 50 + (idx * 60) + 15))

            text_surface = self.small_font.render(info_lines[2], True, (30, 30, 30))
            screen.blit(text_surface, (10, 50 + (idx * 60) + 30))



    def draw_right_sidebar(self, screen, cell_data, settlement_data, selected_cell, filter_name):
        """ Draws a sidebar with information about the selected cell. """
        sidebar_x = config.SCREEN_WIDTH
        sidebar_height = config.SCREEN_HEIGHT
        
        # Draw sidebar background
        pygame.draw.rect(screen, (220, 220, 220), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))  

        # Draw sidebar border (Black, 3px thickness)
        pygame.draw.rect(screen, (80, 80, 80), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)


        # Display title
        title_text = self.large_font.render("Cell Info", True, (30, 30, 30))
        screen.blit(title_text, (sidebar_x + 10, 20))


        if cell_data:
            r, c = selected_cell  # Selected cell coordinates
            

            # Fetch data from terrain maps
            region = config.REGION_NAMES[cell_data["region"]]
            elevation = cell_data["elevation"]
            steepness = cell_data["steepness"]
            traversal_cost = cell_data["traversal_cost"]
            population = cell_data["population"]
            pop_capacity = cell_data["population_capacity"]
            fertility = cell_data["fertility"]
            temperature = cell_data["temperature"]
            rainfall = cell_data["rainfall"]
            resource = cell_data["resource"]

            # List of text entries to display
            cell_info_lines = [
                f"Row: {r}, Col: {c}",
                f"Region: {region.title()}", # First letter of each word is capital
                f"Elevation: {elevation:.2f}",
                f"temperature: {temperature:.2f}",
                f"rainfall: {rainfall:.2f}",
                f"steepness: {steepness:.2f}",
                f"fertility: {fertility:.2f}",
                f"traversal cost: {traversal_cost:.2f}",
                f"population: {population:.2f}",
                f"pop capacity: {pop_capacity:.2f}",
                f"resource: {config.RESOURCE_NAMES[resource].title()}",
            ]

            # Render and display each line
            for i, line in enumerate(cell_info_lines):
                text_surface = self.large_font.render(line, True, (30, 30, 30))
                screen.blit(text_surface, (sidebar_x + 10, 50 + i * 25))
            
            if settlement_data:

                settlement_info_lines = [
                    f"Name: {settlement_data.name}",
                ]

                settlement_offset_y = 100 + len(cell_info_lines) * 25

                title_text = self.large_font.render("Settlement Info", True, (30, 30, 30))
                screen.blit(title_text, (sidebar_x + 10, settlement_offset_y-25))

                for i, line in enumerate(settlement_info_lines):
                    text_surface = self.large_font.render(line, True, (30, 30, 30))
                    screen.blit(text_surface, (sidebar_x + 10, settlement_offset_y + i * 25))
            

            # Display current filter
            filter_text = self.large_font.render(f"Filter: {filter_name}", True, (30, 30, 30))
            screen.blit(filter_text, (sidebar_x + 10, sidebar_height - 40))
    

 


    def draw_hover_highlight(self, hovered_cell, screen, camera_x_pos, camera_y_pos, color=(255, 255, 255, 100)):
        """Draws a semi-transparent highlight over the hovered cell."""
        cell_y, cell_x = hovered_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - camera_x_pos) * config.CELL_SIZE  + config.SIDEBAR_WIDTH
        screen_y = (cell_y - camera_y_pos) * config.CELL_SIZE

        # Create transparent surface for the highlight
        highlight_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(color)

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))


    def draw_selected_cell_border(self, selected_cell, screen, camera_x_pos, camera_y_pos, color=(255, 255, 0)):
        """Draws a border around the selected cell."""
        cell_y, cell_x = selected_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - camera_x_pos) * config.CELL_SIZE  + config.SIDEBAR_WIDTH
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






