import pygame
import config
from ui_components.widgets.textbox import TextBox
from ui_components.widgets.label import Label
from ui_components.widgets.button import Button
from ui_components.widgets.slider import Slider
from ui_components.widgets.component_container import ComponentContainer
from ui_components.widgets.container_list import ContainerList
from ui_components.widgets.line_divider import LineDivider

class Menu:
    def __init__(self, fonts, controller):
        self.component_list = []
        self.fonts = fonts
        self.controller = controller

        self.width = 300
        self.height = 400

        self.rect = pygame.Rect((config.SCREEN_WIDTH+config.SIDEBAR_WIDTH)/2-self.width/2, config.SCREEN_HEIGHT/2-self.height, 300, 400)

        self.show_menu()
    
    def show_menu(self):
        self.component_list = []
        self.component_list.append(Label("Menu", self.fonts.header, self.width))

        hide_menu_button = Button(120, 20, lambda: self.controller.hide_menu(), "Hide Menu", self.fonts.small_font)

        save_map_label = Label("Save map", self.fonts.large_font, config.SIDEBAR_WIDTH)
        save_file_name = TextBox(self.controller, self.fonts.small_font, 150, 20)
        save_button = Button(60, 20, lambda: self.controller.save_map(save_file_name.text), "Save", self.fonts.small_font)

        load_map_label = Label("Load map", self.fonts.large_font, config.SIDEBAR_WIDTH)
        load_file_name = TextBox(self.controller, self.fonts.small_font, 150, 20)
        load_button = Button(60,20, lambda: self.controller.load_map(load_file_name.text), "Load", self.fonts.small_font)

        self.component_list.append(hide_menu_button)

        self.component_list.append(save_map_label)
        self.component_list.append(save_file_name)
        self.component_list.append(save_button)

        self.component_list.append(load_map_label)
        self.component_list.append(load_file_name)
        self.component_list.append(load_button)
    
    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),self.rect)
        pygame.draw.rect(screen, (80,80,80),self.rect, 3)

        y_offset = self.rect.y + 10
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