import pygame
import config
from ui_components.widgets.textbox import TextBox
from ui_components.widgets.label import Label
from ui_components.widgets.button import Button
from ui_components.widgets.slider import Slider
from ui_components.widgets.colour_preview import ColourPreview
from ui_components.widgets.component_container import ComponentContainer
from ui_components.widgets.container_list import ContainerList

class LeftSidebarController:
    def __init__(self, fonts, controller, biome_config):
        self.fonts = fonts
        self.controller = controller
        self.component_list = []
        self.biome_config = biome_config


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
    
    def show_tile_setup_page(self):
        self.component_list = []
        self.component_list.append(
            Label("Tile Setup", self.fonts.large_font, config.SIDEBAR_WIDTH)
        )

        hue_slider = Slider(self.fonts.small_font, 0, 360, config.SIDEBAR_WIDTH - 120)
        sat_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, 100)
        val_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, 100)

        self.component_list.append(ColourPreview(50, 50, hue_slider, sat_slider, val_slider))

        self.component_list.append(Label("Tile name:", self.fonts.large_font, config.SIDEBAR_WIDTH))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 150, 20))

        self.component_list.append(Label("Traversal Cost:", self.fonts.large_font, config.SIDEBAR_WIDTH))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 150, 20, "0"))

        self.component_list.append(Label("Colour:", self.fonts.large_font, config.SIDEBAR_WIDTH))

        self.component_list.append(Label("Hue:", self.fonts.small_font, config.SIDEBAR_WIDTH))
        self.component_list.append(hue_slider)

        self.component_list.append(Label("Saturation:", self.fonts.small_font, config.SIDEBAR_WIDTH))
        self.component_list.append(sat_slider)

        self.component_list.append(Label("Value:", self.fonts.small_font, config.SIDEBAR_WIDTH))
        self.component_list.append(val_slider)

        self.component_list.append(Button(50, 25, lambda: self.controller.add_biome(self.component_list[3].text, self.component_list[8].value, self.component_list[10].value, self.component_list[12].value, int(self.component_list[5].text))))

        
    def show_tile_manager_page(self):
        self.component_list = []
        self.component_list.append(Label("Tile Manager", self.fonts.large_font, config.SIDEBAR_WIDTH))
        biome_container_list = ContainerList(config.SIDEBAR_WIDTH-10, 500)
        for biome in self.biome_config.config:
            biome_container = ComponentContainer(True)
            biome_container.add_component(Label(biome["name"], self.fonts.large_font, 150))
            biome_container.add_component(ColourPreview(20, 20, biome["colour"]["h"], biome["colour"]["s"], biome["colour"]["v"], ))
            biome_container.add_component(Button(50, 20, lambda: self.controller.show_tile_setup_page(), "Edit", self.fonts.small_font))
            biome_container_list.add_container(biome_container)
        
        self.component_list.append(biome_container_list)


    def clear_page(self):
        self.component_list = []

    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        y_offset = 10
        for component in self.component_list:
            if isinstance(component, list):
                x_offset = 0
                for subcomponent in component:
                    subcomponent.draw(screen, subcomponent.left_padding+x_offset, y_offset)
                    x_offset += subcomponent.width
                y_offset += component[0].height
            else:
                component.draw(screen, component.left_padding, y_offset)
                y_offset += component.height




