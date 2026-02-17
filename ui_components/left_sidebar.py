import pygame
import config
from ui_components.widgets.textbox import TextBox
from ui_components.widgets.label import Label
from ui_components.widgets.button import Button
from ui_components.widgets.slider import Slider
from ui_components.widgets.colour_preview import ColourPreview
from ui_components.widgets.component_container import ComponentContainer
from ui_components.widgets.container_list import ContainerList
from ui_components.widgets.line_divider import LineDivider

class LeftSidebarController:
    def __init__(self, fonts, controller, biome_config):
        self.fonts = fonts
        self.controller = controller
        self.component_list = []
        self.biome_config = biome_config

        self.navigation_bar = [[Button(105,20, lambda: self.show_biome_manager_page(), "Biome Page", self.fonts.small_font),
                                Button(125,20, lambda: self.show_location_info_page(), "Location Page", self.fonts.small_font)],
                                LineDivider(config.SIDEBAR_WIDTH-20, 2, 5, 20)]


    def show_region_setup_page(self):
        self.clear_page()
        self.component_list.append(Label("Add Region", self.fonts.header))
        self.component_list.append(Label("Title:", self.fonts.small_font))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 220, 25))
        self.component_list.append(Label("Visible Description:", self.fonts.small_font))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 220, 25))
        self.component_list.append(Label("Hidden Description:", self.fonts.small_font))
        self.component_list.append(TextBox(self.controller, self.fonts.small_font, 220, 25))
        self.component_list.append(Button(50, 25, lambda: self.controller.set_painted_region_info(self.component_list[2].text, self.component_list[4].text, self.component_list[6].text)))
    
    def show_tile_manager_page(self, biome_info = None, biome_index = -1):
        self.clear_page()

        if biome_info and biome_index != -1:
            tile_name = TextBox(self.controller, self.fonts.small_font, 150, 20, biome_info["name"])
            tile_trav_cost = TextBox(self.controller, self.fonts.small_font, 150, 20, str(biome_info["base_traversal_cost"]))
            hue_slider = Slider(self.fonts.small_font, 0, 360, config.SIDEBAR_WIDTH - 120, biome_info["colour"]["h"], top_padding=2)
            sat_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, biome_info["colour"]["s"]*100, top_padding=2)
            val_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, biome_info["colour"]["v"]*100, top_padding=2)
            submit_button = Button(50, 25, lambda: self.controller.edit_biome(biome_index, tile_name.text, hue_slider.value, sat_slider.value/100, val_slider.value/100, float(tile_trav_cost.text)))
        else:
            tile_name = TextBox(self.controller, self.fonts.small_font, 150, 20)
            tile_trav_cost = TextBox(self.controller, self.fonts.small_font, 150, 20, "0")
            hue_slider = Slider(self.fonts.small_font, 0, 360, config.SIDEBAR_WIDTH - 120, top_padding=2)
            sat_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, 100, top_padding=2)
            val_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, 100, top_padding=2)
            submit_button = Button(50, 25, lambda: self.controller.add_biome(tile_name.text, hue_slider.value, sat_slider.value/100, val_slider.value/100, float(tile_trav_cost.text)))

        self.component_list.append(
            Label("Tile Manager", self.fonts.header)
        )

        self.component_list.append(ColourPreview(50, 50, hue_slider, sat_slider, val_slider))

        self.component_list.append(Label("Tile name:", self.fonts.large_font))
        self.component_list.append(tile_name)

        self.component_list.append(Label("Traversal Cost:", self.fonts.large_font))
        self.component_list.append(tile_trav_cost)

        self.component_list.append(Label("Colour:", self.fonts.large_font))

        self.component_list.append(Label("Hue:", self.fonts.small_font, top_padding=2))
        self.component_list.append(hue_slider)

        self.component_list.append(Label("Saturation:", self.fonts.small_font, top_padding=2))
        self.component_list.append(sat_slider)

        self.component_list.append(Label("Value:", self.fonts.small_font, top_padding=2))
        self.component_list.append(val_slider)

        self.component_list.append(submit_button)

        
    def show_biome_manager_page(self):
        self.clear_page()
        self.component_list.extend(self.navigation_bar)
        self.component_list.append(Label("Biome Manager", self.fonts.header))
        biome_container_list = ContainerList(config.SIDEBAR_WIDTH-10, 500)
        for index, biome in enumerate(self.biome_config.config):
            biome_container = ComponentContainer(True)
            biome_container.add_component(Label(biome["name"].capitalize(), self.fonts.large_font, left_padding=5, top_padding=5))
            biome_container.add_component([ColourPreview(20, 20, biome["colour"]["h"], biome["colour"]["s"], biome["colour"]["v"]),
                                        Button(50, 20, lambda b = biome, i = index: self.controller.show_tile_manager_page(b, i), "Edit", self.fonts.small_font, left_padding=5),
                                        Button(50, 20, lambda i = index: self.controller.toggle_tile_paint(i), "Paint", self.fonts.small_font, left_padding=5)])
            biome_container_list.add_container(biome_container)
        
        self.component_list.append(biome_container_list)
        self.component_list.append(Button(100, 20, lambda: self.controller.show_tile_manager_page(), "Add Region", self.fonts.small_font))
    
    def show_location_info_page(self):
        self.clear_page()

        title_label = Label("Location", self.fonts.header, config.SIDEBAR_WIDTH)
        
        if self.controller.selected_cell:
            biome_name_label = Label(self.controller.get_biome_at(self.controller.get_selected_cell()), self.fonts.large_font, top_padding=2)
            scenario_prompt_button = Button(50,20, lambda: self.controller.prompt_scenario(), "Prompt", self.fonts.small_font)
        else:
            biome_name_label = Label("No tile selected", self.fonts.large_font, top_padding=2)
            scenario_prompt_button = None
        
        self.component_list.extend(self.navigation_bar)
        self.component_list.append(title_label)
        self.component_list.append(biome_name_label)
        self.component_list.append(LineDivider(config.SIDEBAR_WIDTH-20, 2))
        if scenario_prompt_button:
            self.component_list.append(scenario_prompt_button)


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




