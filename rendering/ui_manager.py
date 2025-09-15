import pygame
from utils import config
from widgets import InfoBoxList, CollapsibleInfoBox, Button
from functools import partial
from utils.ui_utils import wrap_text


class UIManager:
    def __init__(self, fonts, controller):
        self.controller = controller
        self.left_sidebar = LeftSidebarController(fonts, controller)
        self.right_sidebar = RightSidebarController(fonts, controller)
        self.fonts = fonts
        

    def handle_event(self, event):
        self.left_sidebar.handle_event(event)
        self.right_sidebar.handle_event(event)

    def render_ui(self, screen, world):
        selected_cell = self.controller.selected_cell
        hovered_cell = self.controller.hovered_cell
        settlements_dict = world.get_all_settlements()
        states_dict = world.get_all_states()
        world_event_log = world.get_event_log()
        cell_data, settlement_data, selected_cell, cell_event_log = world.get_cell_data(selected_cell)
        filter_name = self.controller.selected_filter

        active_left_sidebar_screen = self.controller.active_left_sidebar
        active_right_sidebar_screen = self.controller.active_right_sidebar

        if cell_data:
            if cell_data["state"] != 255:
                state_data = states_dict[cell_data["state"]]
            else:
                state_data = None
        else:
            state_data = None

        self.draw_settlements(settlements_dict, screen)

        self.draw_hover_highlight(hovered_cell, screen)

        if selected_cell:
            self.draw_selected_cell_border(selected_cell, screen)

        if active_left_sidebar_screen % 3 == 0:
            self.left_sidebar.show_settlements(settlements_dict)
        elif active_left_sidebar_screen % 3 == 1:
            self.left_sidebar.show_states(states_dict)
        elif active_left_sidebar_screen % 3 == 2:
            self.left_sidebar.show_event_log(world_event_log)
        
        
        if active_right_sidebar_screen % 3 == 0:
            self.right_sidebar.show_cell_info(cell_data)
        elif active_right_sidebar_screen % 3 == 1:
            self.right_sidebar.show_settlement_info(settlement_data, cell_event_log)
        elif active_right_sidebar_screen % 3 == 2:
            self.right_sidebar.show_state_info(state_data)

        self.left_sidebar.draw(screen)
        self.right_sidebar.draw(screen, filter_name)
        

    def draw_settlements(self, settlements_dict, screen):
        for s in settlements_dict.values():
            x = (s.c - self.controller.get_camera_position()[0]) * config.CELL_SIZE + config.SIDEBAR_WIDTH
            y = (s.r - self.controller.get_camera_position()[1]) * config.CELL_SIZE
            pygame.draw.rect(screen, (0, 0, 0), (x, y, config.CELL_SIZE, config.CELL_SIZE))
            text_surface = self.fonts.large_font.render(s.name, True, (30, 30, 30))
            screen.blit(text_surface, (x + 5, y - 5))
    
    
    
    def draw_hover_highlight(self, hovered_cell, screen, color=(255, 255, 255, 100)):
        """Draws a semi-transparent highlight over the hovered cell."""
        cell_y, cell_x = hovered_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - self.controller.get_camera_position()[0]) * config.CELL_SIZE  + config.SIDEBAR_WIDTH
        screen_y = (cell_y - self.controller.get_camera_position()[1]) * config.CELL_SIZE

        # Create transparent surface for the highlight
        highlight_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(color)

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))


    def draw_selected_cell_border(self, selected_cell, screen, color=(255, 255, 0)):
        """Draws a border around the selected cell."""
        cell_y, cell_x = selected_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - self.controller.get_camera_position()[0]) * config.CELL_SIZE  + config.SIDEBAR_WIDTH
        screen_y = (cell_y - self.controller.get_camera_position()[1]) * config.CELL_SIZE

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
    def __init__(self, fonts, controller):
        self.fonts = fonts
        self.controller = controller
        self.title = ""
        self.info_box_list = None

        self.state_info_boxes = {}
        self.settlement_info_boxes = {}
        self.event_info_boxes = {}

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
            box.add_text_link_action(partial(self.controller.select_settlement, s.r, s.c))
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
            box.add_text_link_action(partial(self.controller.select_state, s.id))
            self.info_box_list.add_info_box(box)
    
    def show_event_log(self, event_log):
        self.title = "Event Log"
        self.info_box_list = InfoBoxList(10, 50, config.SIDEBAR_WIDTH - 20)
        for event in event_log:
            if event["tick_count"] not in self.event_info_boxes:
                box = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                self.event_info_boxes[event["tick_count"]] = box
            else:
                box = self.event_info_boxes[event["tick_count"]]

            box.set_info(event['event_type'].title(), {"Tick": str(event['tick_count'])}, {"Location": f"{event['location'][0]}, {event['location'][1]}", "Description": event['event_desc']})
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
    def __init__(self, fonts, controller):
        self.fonts = fonts
        self.controller = controller
        self.title = ""
        self.info_list = {}
        self.buttons = []
    
    def show_settlement_info(self, settlement_data, settlement_events):
        self.buttons = []
        self.title = "Settlement Info"
        if settlement_data:
            self.info_list = {
                "Name": settlement_data.name,
                "Description": "\n".join(wrap_text(settlement_data.description, self.fonts.small_font, config.SIDEBAR_WIDTH - 20)),
                "Improved Resources": "\n",
                "Events": "\n"
            }
            for resource in settlement_data.improved_resources:
                self.info_list["Improved Resources"] += f"{resource.name} ({resource.location[0]}, {resource.location[1]}) ({resource.distance})\n"

            for event in settlement_events:
                self.info_list["Events"] += "\n".join(wrap_text(event['event_desc'], self.fonts.small_font, config.SIDEBAR_WIDTH - 20)) + "\n"
        else:
            self.info_list = {}
            self.buttons.append(Button(config.SCREEN_WIDTH + 10, 50, 170, 25, lambda: self.controller.create_settlement(self.controller.get_selected_cell()), "Create Settlement", self.fonts.small_font))

    def show_state_info(self, state_data):
        self.buttons = []
        self.title = "State Info"
        if state_data:
            self.info_list = {
                "Name": state_data.name,
                "Tile Capacity": f"{state_data.tile_capacity:.1f}",
                "Tile Count": f"{state_data.tile_count:.0f}"
            }
        else:
            self.info_list = {}
            self.buttons.append(Button(config.SCREEN_WIDTH + 10, 50, 170, 25, lambda: self.controller.create_state(self.controller.get_selected_cell()), "Create State", self.fonts.small_font))
    
    def show_cell_info(self, cell_data):
        self.buttons = []
        self.title = "Cell Info"
        if cell_data:
            self.info_list = {
                "Row": self.controller.get_selected_cell()[0],
                "Col": self.controller.get_selected_cell()[1],
                "Region": config.REGION_RULES[cell_data["region"]]["name"].title(),
                "Elevation": f"{cell_data['elevation']:.2f}",
                "Temperature": f"{cell_data['temperature']:.2f}",
                "Rainfall": f"{cell_data['rainfall']:.2f}",
                "Steepness": f"{cell_data['steepness']:.2f}",
                "Fertility": f"{cell_data['fertility']:.2f}",
                "Traversal Cost": f"{cell_data['traversal_cost']:.2f}",
                "Population": f"{cell_data['population']:.2f}",
                "Population Capacity": f"{cell_data['population_capacity']:.2f}",
                "Resource": config.RESOURCE_NAMES[cell_data['resource']].title(),
                "State": cell_data["state"],
                "Settlement Distance": cell_data['settlement_distance'],
                "Flip Probability": f"{cell_data['flip_probability']:.3f}",
                "Decay Probability": f"{cell_data['decay_probability']:.3f}",
                "Neighbor Counts": cell_data["neighbor_counts"]
            }
        else:
            self.info_list = {}
    
            
        
    def draw(self, screen, filter_name):
        # Draw sidebar background
        pygame.draw.rect(screen, (220, 220, 220), (config.SCREEN_WIDTH, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))  

        # Draw sidebar border (Black, 3px thickness)
        pygame.draw.rect(screen, (80, 80, 80), (config.SCREEN_WIDTH, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)


        title_text = self.fonts.large_font.render(self.title, True, (30, 30, 30))
        screen.blit(title_text, (config.SCREEN_WIDTH + 10, 20))
        
        for i, (label, value) in enumerate(self.info_list.items()):
            text_surface = self.fonts.small_font.render(f"{label}: {value}", True, (30, 30, 30))
            screen.blit(text_surface, (config.SCREEN_WIDTH + 10, 50 + i * 20))
        
        for button in self.buttons:
            button.draw(screen)
        
        filter_text = self.fonts.small_font.render(f"Filter: {filter_name}", True, (30, 30, 30))
        screen.blit(filter_text, (config.SCREEN_WIDTH + 10, config.SCREEN_HEIGHT - 40))
    
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)