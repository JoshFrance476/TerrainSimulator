import pygame
import config

class RightSidebarController:
    def __init__(self, fonts, controller):
        self.fonts = fonts
        self.controller = controller
        self.title = ""
        self.info_list = {}
        self.buttons = []
        self.textbox = None
    

    def show_cell_info(self, cell_data):
        self.buttons = []
        self.textbox = None
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
                "Traversal Cost": f"{cell_data['traversal_cost']:.2f}",
                "Colour": tuple(round(float(x),2) for x in cell_data["colour"]),
                "Sea Proximity": cell_data['sea_proximity']
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
        
        if self.textbox:
            self.textbox.draw(screen)
        
        filter_text = self.fonts.small_font.render(f"Filter: {filter_name}", True, (30, 30, 30))
        screen.blit(filter_text, (config.SCREEN_WIDTH + 10, config.SCREEN_HEIGHT - 40))
    
    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)
        if self.textbox:
            self.textbox.handle_mouse_input(event)