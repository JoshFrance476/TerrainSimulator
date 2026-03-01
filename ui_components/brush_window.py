import pygame
import config
from ui_components.widgets.slider import Slider
from ui_components.widgets.button import Button

class BrushWindow:
    def __init__(self, fonts, interaction_system):
        self.component_list = []
        self.fonts = fonts
        self.interaction_system = interaction_system

        self.rect = pygame.Rect(config.SIDEBAR_WIDTH, 0, 200, 60)

        self.brush_size_slider = Slider(self.fonts.small_font, 1, 10, 100, top_padding=10)
        self.submit_button = Button(50, 20, lambda: self.interaction_system.set_brush_attributes(size=self.brush_size_slider.value), "Set", self.fonts.small_font)
        self.component_list.append(self.brush_size_slider)
        self.component_list.append(self.submit_button)

    def set_attributes(self, attributes_dict):
        self.brush_size_slider.default_value = attributes_dict['size']

    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220), self.rect)
        pygame.draw.rect(screen, (80,80,80), self.rect, 3)

        y_offset = self.rect.y
        for component in self.component_list:
            if isinstance(component, list):
                x_offset = self.rect.x
                for subcomponent in component:
                    subcomponent.draw(screen, subcomponent.left_padding+x_offset, y_offset)
                    x_offset += subcomponent.width
                y_offset += component[0].height
            else:
                component.draw(screen, component.left_padding+self.rect.x, y_offset)
                y_offset += component.height
