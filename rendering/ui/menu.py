import pygame
import config
from rendering.ui.widgets.textbox import TextBox
from rendering.ui.widgets.label import Label
from rendering.ui.widgets.button import Button


class Menu:
    def __init__(self, fonts, interaction_system, state):
        self.component_list = []
        self.fonts = fonts
        self.interaction_system = interaction_system
        self.state = state

        self.width = 300
        self.height = 400

        self.rect = pygame.Rect((config.SCREEN_WIDTH+config.SIDEBAR_WIDTH)/2-self.width/2, config.SCREEN_HEIGHT/2-self.height, 300, 400)

        self.show_menu()
    
    def show_menu(self):
        self.component_list = []
        self.component_list.append(Label("Menu", self.fonts.header, self.width))

        hide_menu_button = Button(120, 20, lambda: setattr(self.state, "show_menu", False), "Hide Menu", self.fonts.small_font)

        save_map_label = Label("Save map", self.fonts.large_font, config.SIDEBAR_WIDTH)
        save_file_name = TextBox(self.interaction_system, self.fonts.small_font, 150, 20)
        save_button = Button(60, 20, lambda: self.interaction_system.save_map(save_file_name.text), "Save", self.fonts.small_font)

        load_map_label = Label("Load map", self.fonts.large_font, config.SIDEBAR_WIDTH)
        load_file_name = TextBox(self.interaction_system, self.fonts.small_font, 150, 20)
        load_button = Button(60,20, lambda: self.interaction_system.load_map(load_file_name.text), "Load", self.fonts.small_font)

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