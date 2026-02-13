import pygame
import config
from ui_components.widgets.textbox import TextBox
from ui_components.widgets.label import Label
from ui_components.widgets.button import Button

class LeftSidebarController:
    def __init__(self, fonts, controller):
        self.fonts = fonts
        self.controller = controller
        self.component_list = []


    def show_region_setup_page(self):
        self.component_list = []
        self.component_list.append(Label("Add Region", self.fonts.large_font, config.SIDEBAR_WIDTH))
        self.component_list.append(Label("Title:", self.fonts.small_font, config.SIDEBAR_WIDTH))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 220, 25))
        self.component_list.append(Label("Visible Description:", self.fonts.small_font, config.SIDEBAR_WIDTH))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 220, 25))
        self.component_list.append(Label("Hidden Description:", self.fonts.small_font, config.SIDEBAR_WIDTH))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 220, 25))
        self.component_list.append(Button(50, 25, lambda: self.controller.set_painted_region_info(self.component_list[2].text, self.component_list[4].text, self.component_list[6].text)))
    
    def clear_page(self):
        self.component_list = []

    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        y_offset = 10
        for component in self.component_list:
            component.draw(screen, 10, y_offset)
            y_offset += component.height




