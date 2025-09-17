import pygame
import config
from ui_components.widgets import Button
from utils.ui_utils import wrap_text

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
                "Neighbor Counts": cell_data["neighbor_counts"],
                "Colour": tuple(int(x) for x in cell_data["colour"])
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