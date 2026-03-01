from ui_components.widgets.tooltip import Tooltip
from ui_components.widgets.label import Label
import pygame

class TooltipManager:
    def __init__(self, fonts, world, biome_config):
        self.world = world
        self.biome_config = biome_config
        self.fonts = fonts

        self.tooltip_list = []
    
    def generate_tooltip_list(self, location):
        self.tooltip_list = []
        regions = self.world.get_regions_at_location(location)

        biome = self.biome_config.biomes[self.world.get_cell_data(location)["biome"]]["name"].title()
        tooltip = Tooltip(self.fonts.small_font)
        tooltip.add_components([Label(biome, self.fonts.large_font, tooltip.max_width, left_padding=0)])
        self.tooltip_list.append(tooltip)

        for region in regions:
            tooltip = Tooltip(self.fonts.small_font)
            if region.title != "":
                tooltip.add_components([Label(region.title, self.fonts.large_font, tooltip.max_width, left_padding=0)])
            if region.visible_desc != "":
                tooltip.add_components([Label(region.visible_desc, self.fonts.small_font, tooltip.max_width, left_padding=0)])
            self.tooltip_list.append(tooltip)
    
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        y_offset = 5
        for tooltip in self.tooltip_list:
            if tooltip.components:
                tooltip.draw(screen, mouse_pos[0], mouse_pos[1]-y_offset-tooltip.height)
                y_offset += tooltip.height + 5