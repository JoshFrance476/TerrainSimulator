import pygame
from utils import config
from widgets import InfoBoxList, InfoBox, CollapsibleInfoBox



class UIManager:
    def __init__(self, fonts):
        self.left_sidebar = LeftSidebarController(fonts)
        self.right_sidebar = RightSidebarController(fonts)
        self.fonts = fonts

    def handle_event(self, event):
        self.left_sidebar.handle_event(event)

    def render_ui(self, screen, cell_data, active_screens, settlements_dict, states_dict, camera_x, camera_y, filter, relevant_cells):
        active_left_sidebar_screen, active_right_sidebar_screen = active_screens
        cell_data, settlement_data, selected_cell = cell_data
        if cell_data:
            if cell_data["state"] != 255:
                state_data = states_dict[cell_data["state"]]
            else:
                state_data = None
        else:
            state_data = None

        self.draw_settlements(settlements_dict, screen, camera_x, camera_y)

        if active_left_sidebar_screen % 2 == 0:
            self.left_sidebar.show_settlements(settlements_dict)
        else:
            self.left_sidebar.show_states(states_dict)

        self.left_sidebar.draw(screen)
        selected_cell, hovered_cell = relevant_cells
        self.draw_hover_highlight(hovered_cell, screen, camera_x, camera_y)
        self.right_sidebar.draw(screen, active_right_sidebar_screen, cell_data, settlement_data, state_data, filter, selected_cell)
        if selected_cell:
            self.draw_selected_cell_border(selected_cell, screen, camera_x, camera_y)
    
    def draw_settlements(self, settlements_dict, screen, camera_x, camera_y):
        for s in settlements_dict.values():
            x = (s.c - camera_x) * config.CELL_SIZE + config.SIDEBAR_WIDTH
            y = (s.r - camera_y) * config.CELL_SIZE
            pygame.draw.rect(screen, (0, 0, 0), (x, y, config.CELL_SIZE, config.CELL_SIZE))
            text_surface = self.fonts.large_font.render(s.name, True, (30, 30, 30))
            screen.blit(text_surface, (x + 5, y - 5))
    
    
    
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


class LeftSidebarController:
    def __init__(self, fonts):
        self.fonts = fonts
        self.title = ""
        self.info_box_list = None

        self.state_info_boxes = {}
        self.settlement_info_boxes = {}

    def show_settlements(self, settlements_dict):
        self.title = "Settlements"
        self.info_box_list = InfoBoxList(10, 50, config.SIDEBAR_WIDTH - 20)
        for s in settlements_dict.values():
            if s.id not in self.settlement_info_boxes:
                box = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                self.settlement_info_boxes[s.id] = box
            else:
                box = self.settlement_info_boxes[s.id]

            box.set_info(s.name, {"Location": f"{s.r}, {s.c}"}, {"Population": f"{s.population:.2f}"})
            self.info_box_list.add_info_box(box)

    def show_states(self, states_dict):
        self.title = "States"
        self.info_box_list = InfoBoxList(10, 50, config.SIDEBAR_WIDTH - 20)
        for s in states_dict.values():
            if s.id not in self.state_info_boxes:
                box = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                self.state_info_boxes[s.id] = box
            else:
                box = self.state_info_boxes[s.id]

            box.set_info(str(s.name), {"Tile Capacity": f"{s.tile_capacity:.0f}"}, {"Tile Count": s.tile_count})
            self.info_box_list.add_info_box(box)

    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        title_text = self.fonts.large_font.render(self.title, True, (30,30,30))
        screen.blit(title_text, (10, 20))

        if self.info_box_list:
            self.info_box_list.draw(screen)

    def handle_event(self, event):
        if self.info_box_list:
            self.info_box_list.handle_event(event)


class RightSidebarController:
    def __init__(self, fonts):
        self.fonts = fonts


    def draw(self, screen, active_right_sidebar_screen, cell_data, settlement_data, state_data, filter_name, selected_cell):
        # Draw sidebar background
        pygame.draw.rect(screen, (220, 220, 220), (self.sidebar_x, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))  

        # Draw sidebar border (Black, 3px thickness)
        pygame.draw.rect(screen, (80, 80, 80), (self.sidebar_x, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        

        if active_right_sidebar_screen % 3 == 0:
            title, info_list = self.unpack_cell_info(cell_data, selected_cell)
        elif active_right_sidebar_screen % 3 == 1:
            title, info_list = self.unpack_settlement_info(settlement_data)
        elif active_right_sidebar_screen % 3 == 2:
            title, info_list = self.unpack_state_info(state_data)
        
         # Display title
        title_text = self.fonts.large_font.render(title, True, (30, 30, 30))
        screen.blit(title_text, (self.sidebar_x + 10, 20))
        
        for i, line in enumerate(info_list):
            text_surface = self.fonts.large_font.render(line, True, (30, 30, 30))
            screen.blit(text_surface, (self.sidebar_x + 10, 50 + i * 25))
        
        filter_text = self.fonts.large_font.render(f"Filter: {filter_name}", True, (30, 30, 30))
        screen.blit(filter_text, (self.sidebar_x + 10, self.sidebar_height - 40))
    
    def unpack_settlement_info(self, settlement_data):
        settlement_info_lines = []
        title = "Settlement Info"
        if settlement_data:
            settlement_info_lines = [
                f"Name: {settlement_data.name}",
                f"Resources:"
            ]
                
            settlement_resources = settlement_data.resources

            for resource, count in settlement_resources.items():
                settlement_info_lines.append(f"{resource.title()}: {count}")

        return title, settlement_info_lines

    def unpack_state_info(self, state_data):
        state_info_lines = []
        title = "State Info"
        if state_data:
            state_info_lines = [
                f"Name: {state_data.name}",
                f"Tile Capacity: {state_data.tile_capacity}",
                f"Tile Count: {state_data.tile_count}"
            ]

        return title, state_info_lines

    def unpack_cell_info(self, cell_data, selected_cell):

        cell_info_lines = []
        title = "Cell Info" 
        if cell_data:
            r, c = selected_cell
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
            state = cell_data["state"]
            settlement_distance = cell_data["settlement_distance"]
            flip_probability = cell_data["flip_probability"]
            decay_probability = cell_data["decay_probability"]
            neighbor_counts = cell_data["neighbor_counts"]

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
                f"state: {state}",
                f"settlement dist: {settlement_distance}",
                f"flip prob: {flip_probability:.3f}",
                f"decay prob: {decay_probability:.3f}",
                f"neighbor counts: {neighbor_counts}"
            ]
        
        return title, cell_info_lines