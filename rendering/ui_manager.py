import pygame
import config
from ui_components.left_sidebar import LeftSidebarController
from ui_components.right_sidebar import RightSidebarController


class UIManager:
    def __init__(self, controller, fonts, world):
        self.controller = controller
        self.left_sidebar = LeftSidebarController(fonts, controller)
        self.right_sidebar = RightSidebarController(fonts, controller)
        self.world = world
        self.fonts = fonts
        
    def get_clicked_component(self, event_pos):
        clicked_component = False
        for component in self.left_sidebar.component_list:
            if component.collide_with(event_pos):
                clicked_component = component
        #for component in self.right_sidebar.component_list:
        #    if component.collide_with(event_pos):
        #        clicked_component = component
        return clicked_component


    def render_ui(self, screen):
        selected_cell = self.controller.selected_cell
        hovered_cell = self.controller.hovered_cell
        cell_data, selected_cell = self.world.get_cell_data(selected_cell)
        filter_name = self.controller.selected_filter

        if hovered_cell:
            self.draw_hover_highlight(hovered_cell, screen)

        if selected_cell:
            self.draw_selected_cell_border(selected_cell, screen)
        
        self.right_sidebar.show_cell_info(cell_data)

        self.left_sidebar.draw(screen)
        self.right_sidebar.draw(screen, filter_name)


    
    
    
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


