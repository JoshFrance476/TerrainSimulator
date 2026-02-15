import pygame
import config
from ui_components.widgets.label import Label
from ui_components.widgets.line_divider import LineDivider


class RightSidebarController:
    def __init__(self, fonts, controller, biome_config):
        self.fonts = fonts
        self.controller = controller
        self.component_list = []
        self.biome_config = biome_config

    

    def show_location_info_page(self):
        self.component_list = []
        self.component_list.append(Label("Location", self.fonts.header, config.SIDEBAR_WIDTH))
        self.component_list.append(Label(self.controller.get_biome_at(self.controller.get_selected_cell()), self.fonts.large_font, top_padding=2))
        self.component_list.append(LineDivider(config.SIDEBAR_WIDTH-20, 2))
    
        
    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (config.SCREEN_WIDTH, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (config.SCREEN_WIDTH, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        y_offset = 10
        for component in self.component_list:
            if isinstance(component, list):
                x_offset = config.SCREEN_WIDTH
                for subcomponent in component:
                    subcomponent.draw(screen, subcomponent.left_padding+x_offset, y_offset)
                    x_offset += subcomponent.width
                y_offset += component[0].height
            else:
                if hasattr(component, "top_padding"):
                    y_offset += component.top_padding
                component.draw(screen, config.SCREEN_WIDTH+component.left_padding, y_offset)
                y_offset += component.height
