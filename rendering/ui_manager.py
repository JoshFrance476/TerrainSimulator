import pygame
import config
from ui_components.left_sidebar import LeftSidebarController
from ui_components.right_sidebar import RightSidebarController


class UIManager:
    def __init__(self, fonts, controller):
        self.controller = controller
        self.left_sidebar = LeftSidebarController(fonts, controller)
        self.right_sidebar = RightSidebarController(fonts, controller)
        self.fonts = fonts
        

    def handle_event(self, event):
        self.left_sidebar.handle_event(event)
        self.right_sidebar.handle_event(event)

    def render_ui(self, screen, world):
        selected_cell = self.controller.selected_cell
        hovered_cell = self.controller.hovered_cell
        settlements_dict = world.get_all_settlements()
        states_dict = world.get_all_states()
        world_event_log = world.get_event_log()
        cell_data, settlement_data, selected_cell, cell_event_log = world.get_cell_data(selected_cell)
        filter_name = self.controller.selected_filter

        active_left_sidebar_screen = self.controller.active_left_sidebar
        active_right_sidebar_screen = self.controller.active_right_sidebar

        if cell_data:
            if cell_data["state"] != 255:
                state_data = states_dict[cell_data["state"]]
            else:
                state_data = None
        else:
            state_data = None

        self.draw_settlements(settlements_dict, screen)

        self.draw_hover_highlight(hovered_cell, screen)

        if selected_cell:
            self.draw_selected_cell_border(selected_cell, screen)

        if active_left_sidebar_screen % 3 == 0:
            self.left_sidebar.show_settlements(settlements_dict)
        elif active_left_sidebar_screen % 3 == 1:
            self.left_sidebar.show_states(states_dict)
        elif active_left_sidebar_screen % 3 == 2:
            self.left_sidebar.show_event_log(world_event_log)
        
        
        if active_right_sidebar_screen % 3 == 0:
            self.right_sidebar.show_cell_info(cell_data)
        elif active_right_sidebar_screen % 3 == 1:
            self.right_sidebar.show_settlement_info(settlement_data, cell_event_log)
        elif active_right_sidebar_screen % 3 == 2:
            self.right_sidebar.show_state_info(state_data)

        self.left_sidebar.draw(screen)
        self.right_sidebar.draw(screen, filter_name)
        

    def draw_settlements(self, settlements_dict, screen):
        for s in settlements_dict.values():
            x = (s.c - self.controller.get_camera_position()[0]) * config.CELL_SIZE + config.SIDEBAR_WIDTH
            y = (s.r - self.controller.get_camera_position()[1]) * config.CELL_SIZE
            pygame.draw.rect(screen, (0, 0, 0), (x, y, config.CELL_SIZE, config.CELL_SIZE))
            text_surface = self.fonts.large_font.render(s.name, True, (30, 30, 30))
            screen.blit(text_surface, (x + 5, y - 5))
    
    
    
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


