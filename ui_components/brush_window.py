import pygame
import config
from ui_components.widgets.slider import Slider
from ui_components.widgets.button import Button
from ui_components.widgets.label import Label
from ui_components.widgets.checkbox import Checkbox
from ui_components.widgets.line_divider import LineDivider
from app_state import InteractionType

class BrushWindow:
    def __init__(self, fonts, interaction_system):
        self.component_list = []
        self.fonts = fonts
        self.interaction_system = interaction_system

        self.width = 200
        self.height = 100

        self.rect = pygame.Rect(config.SIDEBAR_WIDTH, 0, self.width, self.height)
    
    def show_page(self, page_name):
        match page_name:
            case InteractionType.PAINT_REGION:
                self.show_region_brush()
            case InteractionType.PAINT_TILE:
                self.show_biome_brush()
            case InteractionType.EDIT_ELEVATION:
                self.show_elevation_brush()
    
    def show_biome_brush(self):
        self.component_list = []
        title = Label("Biome Brush", self.fonts.large_font, top_padding=5, left_padding=2)
        self.brush_size_slider = Slider(self.fonts.small_font, 1, 10, 100, top_padding=10)
        submit_button = Button(50, 20, lambda: self.interaction_system.set_brush_attributes(size=self.brush_size_slider.value), "Set", self.fonts.small_font)
        exit_button = Button(20,20, lambda: self.interaction_system.toggle_view_tile(), "X", self.fonts.small_font, left_padding=0)
        toggle_brush_button = Button(50, 20, lambda: self.interaction_system.toggle_brush_mode(), "Brush", self.fonts.small_font)
        toggle_fill_button = Button(50, 20, lambda: self.interaction_system.toggle_fill_mode(), "Fill", self.fonts.small_font)
        self.component_list.append([exit_button, title])
        self.component_list.append(self.brush_size_slider)
        self.component_list.append([toggle_brush_button, toggle_fill_button])
        self.component_list.append(submit_button)
    
    def show_elevation_brush(self):
        self.component_list = []
        title = Label("Elevation Brush", self.fonts.large_font, top_padding=5, left_padding=2)
        self.brush_size_slider = Slider(self.fonts.small_font, 1, 10, 100, top_padding=10)
        checkbox_label = Label("Biome overwrite:", self.fonts.small_font)
        checkbox = Checkbox(20, 20, lambda checkbox_state: self.interaction_system.toggle_elevation_updates_biome(checkbox_state), left_padding=10)
        line_divider = LineDivider(self.width, thickness=0, top_padding=8)
        submit_button = Button(50, 20, lambda: self.interaction_system.set_brush_attributes(size=self.brush_size_slider.value), "Set", self.fonts.small_font)

        self.component_list.append([Button(20,20, lambda: self.interaction_system.toggle_view_tile(), "X", self.fonts.small_font, left_padding=0), title])
        self.component_list.append(self.brush_size_slider)
        self.component_list.append(line_divider)
        self.component_list.append([checkbox_label, checkbox])
        self.component_list.append(submit_button)
    
    def show_region_brush(self):
        self.component_list = []
        title = Label("Region Brush", self.fonts.large_font, top_padding=5, left_padding=2)
        self.brush_size_slider = Slider(self.fonts.small_font, 1, 10, 100, top_padding=10)
        submit_button = Button(50, 20, lambda: self.interaction_system.set_brush_attributes(size=self.brush_size_slider.value), "Set", self.fonts.small_font)
        self.component_list.append([Button(20,20, lambda: self.interaction_system.toggle_view_tile(), "X", self.fonts.small_font, left_padding=0), title])
        self.component_list.append(self.brush_size_slider)
        self.component_list.append(submit_button)

    def set_attributes(self, attributes_dict):
        self.brush_size_slider.value = attributes_dict['size']

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
