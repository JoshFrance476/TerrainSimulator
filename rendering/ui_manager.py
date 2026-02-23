import pygame
import config
from ui_components.left_sidebar import LeftSidebarController
from ui_components.right_sidebar import RightSidebarController
from ui_components.menu import Menu
from ui_components.widgets.tooltip import Tooltip
from ui_components.widgets.label import Label
from ui_components.widgets.container_list import ContainerList


class UIManager:
    def __init__(self, controller, fonts, world, biome_config):
        self.controller = controller
        self.biome_config = biome_config
        self.left_sidebar = LeftSidebarController(fonts, controller, biome_config)
        self.right_sidebar = RightSidebarController(fonts, controller, biome_config)
        self.menu = Menu(fonts, controller)
        self.world = world
        self.fonts = fonts

        self.show_menu = False
    
    def render_ui(self, screen):
        selected_cell = self.controller.selected_cell
        hovered_cell = self.controller.hovered_cell


        if selected_cell:
                self.draw_selected_cell_border(selected_cell, screen)
        
        self.left_sidebar.draw(screen)
        self.right_sidebar.draw(screen)

        if self.mouse_on_map():
            if hovered_cell:
                self.draw_hover_highlight(hovered_cell, screen)
            
            self.draw_tooltip_list(screen)

        if self.show_menu:
            self.menu.draw(screen)

        
    def get_clicked_component(self, event_pos):
        ui_component_list = []
        ui_component_list.extend(self.left_sidebar.component_list)
        ui_component_list.extend(self.right_sidebar.component_list)
        if self.show_menu:
            ui_component_list.extend(self.menu.component_list)
        for component in ui_component_list:

            if isinstance(component, list):
                for subcomponent in component:
                    if hasattr(subcomponent, "collide_with"):
                        if subcomponent.collide_with(event_pos):
                            return subcomponent
                    
            if isinstance(component, ContainerList):
                for subcomponent in component.containers:
                    for subsubcomponent in subcomponent.components:
                        if isinstance(subsubcomponent, list):
                            for subsubsubcomponent in subsubcomponent:
                                if hasattr(subsubsubcomponent, "collide_with"):
                                    if subsubsubcomponent.collide_with(event_pos):
                                        return subsubsubcomponent
            
            if hasattr(component, "collide_with"):
                if component.collide_with(event_pos):
                    if isinstance(component, ContainerList):
                        container_list = component
                        for component_container in container_list.containers:
                            for container_component in component_container.components:
                                if hasattr(container_component, "collide_with"):
                                    if container_component.collide_with(event_pos):
                                        return container_component
                    return component
                    
        return None


    def show_region_setup_page(self):
        self.left_sidebar.show_region_setup_page()
    
    def show_tile_manager_page(self, biome_info, index):
        self.left_sidebar.show_tile_manager_page(biome_info, index)
    
    def show_biome_manager_page(self):
        self.left_sidebar.show_biome_manager_page()
    
    def show_location_info_page(self):
        self.left_sidebar.show_location_info_page()
    
    def show_current_scenario_screen(self):
        self.right_sidebar.show_current_scenario_screen()
    
    def clear_left_page(self):
        self.left_sidebar.clear_page()


    def render_tooltip(self, location):
        self.tooltip_list = []
        regions = self.world.region_manager.get_regions_at_location(location)

        biome = self.biome_config.biomes[self.world.get_cell_data(location)["biome"]]["name"].title()
        tooltip = Tooltip(self.controller, self.fonts.small_font)
        tooltip.add_components([Label(biome, self.fonts.large_font, tooltip.max_width, left_padding=0)])
        self.tooltip_list.append(tooltip)

        for region in regions:
            tooltip = Tooltip(self.controller, self.fonts.small_font)
            if region.title != "":
                tooltip.add_components([Label(region.title, self.fonts.large_font, tooltip.max_width, left_padding=0)])
            if region.visible_desc != "":
                tooltip.add_components([Label(region.visible_desc, self.fonts.small_font, tooltip.max_width, left_padding=0)])
            self.tooltip_list.append(tooltip)
    
    def draw_fps_counter(self, screen, fps):
        pygame.draw.rect(screen, (220,220,220),
                         (config.SCREEN_WIDTH-58, config.SCREEN_HEIGHT-30, 60, 30))
        pygame.draw.rect(screen, (80,80,80),
                         (config.SCREEN_WIDTH-58, config.SCREEN_HEIGHT-30, 60, 30), 3)
        fps_text = self.fonts.small_font.render(str(fps), True, (30,30,30))
        screen.blit(fps_text, (config.SCREEN_WIDTH-38, config.SCREEN_HEIGHT-23))

    
    def draw_tooltip_list(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        y_offset = 5
        for tooltip in self.tooltip_list:
            if tooltip.components:
                tooltip.draw(screen, mouse_pos[0], mouse_pos[1]-y_offset-tooltip.height)
                y_offset += tooltip.height + 5
    
    def draw_hover_highlight(self, hovered_cell, screen, color=(255, 255, 255, 100)):
        """Draws a semi-transparent highlight over the hovered cell."""
        cell_y, cell_x = hovered_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - self.controller.get_camera_position()[0]) * config.CELL_SIZE  + config.SIDEBAR_WIDTH
        screen_y = (cell_y - self.controller.get_camera_position()[1]) * config.CELL_SIZE

        # Create transparent surface for the highlight
        highlight_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(color)

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))


    def draw_selected_cell_border(self, selected_cell, screen, color=(255, 255, 0)):
        """Draws a border around the selected cell."""
        cell_y, cell_x = selected_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - self.controller.get_camera_position()[0]) * config.CELL_SIZE  + config.SIDEBAR_WIDTH
        screen_y = (cell_y - self.controller.get_camera_position()[1]) * config.CELL_SIZE

        # Create transparent surface for the border
        highlight_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        
        
        # Draw rectangle border with scaled thickness
        pygame.draw.rect(
            highlight_surface,
            color,
            (0, 0, config.CELL_SIZE, config.CELL_SIZE),
            1
        )

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))

    def mouse_on_map(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        collide_with_menu = False
        if self.show_menu:
            if self.menu.rect.collidepoint(mouse_x, mouse_y):
                collide_with_menu = True
        return mouse_x > config.SIDEBAR_WIDTH and mouse_x < config.SCREEN_WIDTH and mouse_y > 0 and mouse_y < config.SCREEN_HEIGHT and not collide_with_menu
