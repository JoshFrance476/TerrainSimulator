import pygame
import config
from ui_components.widgets.textbox import TextBox

class LeftSidebarController:
    def __init__(self, fonts, controller):
        self.fonts = fonts
        self.controller = controller
        self.title = ""
        self.component_list = []

        self.show_add_region_page()

    def show_add_region_page(self):
        self.component_list = []
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 220, 25))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 220, 25))

    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        title_text = self.fonts.large_font.render(self.title, True, (30,30,30))
        screen.blit(title_text, (10, 20))

        y_offset = 10
        for component in self.component_list:
            if isinstance(component, TextBox):
                component.draw(screen, 10, y_offset)
            y_offset += 30




