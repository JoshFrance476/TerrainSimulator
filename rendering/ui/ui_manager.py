import pygame
import config
from rendering.ui.left_sidebar import LeftSidebarController
from rendering.ui.right_sidebar import RightSidebarController
from rendering.ui.menu import Menu
from rendering.ui.tooltip_manager import TooltipManager
from rendering.ui.widgets.label import Label
from rendering.ui.widgets.container_list import ContainerList
from rendering.ui.brush_window import BrushWindow
from app.app_state import InteractionType, LeftPage, RightPage


class UIManager:
    def __init__(self, state, camera, storyteller, fonts, world, get_brush_attributes, generate_map_func, load_file_func, save_file_func):
        self.state = state
        self.camera = camera
        self.interaction_system = None
        self.storyteller = storyteller
        self.world = world
        self.fonts = fonts

        self._last_left_page = None

        self._current_brush_type = None

        self._last_selected_cell = None
        self._last_hovered_cell = None

        self.get_brush_attributes = get_brush_attributes

        self.generate_map_func = generate_map_func
        self.load_file_func = load_file_func
        self.save_file_func = save_file_func

    def set_interaction_system(self, interaction_system):
        self.interaction_system = interaction_system
        self.left_sidebar = LeftSidebarController(self.fonts, self.state, self.world, self.interaction_system, self.storyteller)
        self.right_sidebar = RightSidebarController(self.fonts, self.storyteller, self.interaction_system)
        self.menu = Menu(self.fonts, self.interaction_system, self.state, self.generate_map_func, self.load_file_func, self.save_file_func)
        self.tooltips = TooltipManager(self.fonts, self.world)
        self.brush_window = BrushWindow(self.fonts, self.interaction_system)

        self.right_sidebar.show_current_scenario_screen()
       
    def render_ui(self, screen):
        selected_cell = self.state.selected_cell
        hovered_cell = self.state.hovered_cell

        if self._last_left_page != self.state.left_page:
            self.left_sidebar.show_page(self.state.left_page)
            self._last_left_page = self.state.left_page
        
        if self._last_selected_cell != selected_cell and self.state.left_page == LeftPage.VIEW_LOCATION:
            self.left_sidebar.show_page(self.state.left_page)
            self._last_selected_cell = selected_cell
        

        if self.state.update_right_page:
            self.right_sidebar.show_current_scenario_screen()
            self.state.update_right_page = False
        

        if selected_cell:
                self.draw_selected_cell_border(selected_cell, screen)

        self.left_sidebar.draw(screen)
        self.right_sidebar.draw(screen)

        if self.mouse_on_map():
            if hovered_cell:
                self.draw_hover_highlight(hovered_cell, screen)
            
            if self._last_hovered_cell != hovered_cell:
                self.tooltips.generate_tooltip_list(hovered_cell)
                self._last_hovered_cell = hovered_cell
            self.tooltips.draw(screen)
        
        if self.state.show_menu:
            self.menu.draw(screen)
        
        if self.state.interaction_type in {InteractionType.PAINT_REGION, InteractionType.PAINT_TILE, InteractionType.EDIT_ELEVATION}:
            if self.state.interaction_type is not self._current_brush_type:
                self.brush_window.show_page(self.state.interaction_type)
                self._current_brush_type = self.state.interaction_type
                self.brush_window.set_attributes(self.get_brush_attributes())
            self.brush_window.draw(screen)


        
    def get_clicked_component(self, event_pos):
        ui_component_list = []
        ui_component_list.extend(self.left_sidebar.component_list)
        ui_component_list.extend(self.right_sidebar.component_list)

        if self.state.show_menu:
            ui_component_list.extend(self.menu.component_list)
        
        if self.state.interaction_type in {InteractionType.PAINT_REGION, InteractionType.PAINT_TILE, InteractionType.EDIT_ELEVATION}:
            ui_component_list.extend(self.brush_window.component_list)
        
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
    
    def mouse_on_map(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.state.show_menu:
            if self.menu.rect.collidepoint(mouse_x, mouse_y):
                return False
        if self.state.interaction_type in {InteractionType.PAINT_REGION, InteractionType.PAINT_TILE, InteractionType.EDIT_ELEVATION}:
            if self.brush_window.rect.collidepoint(mouse_x, mouse_y):
                return False
        return mouse_x > config.SIDEBAR_WIDTH and mouse_x < config.SCREEN_WIDTH and mouse_y > 0 and mouse_y < config.SCREEN_HEIGHT

    def draw_fps_counter(self, screen, fps):
        pygame.draw.rect(screen, (220,220,220),
                         (config.SCREEN_WIDTH-58, config.SCREEN_HEIGHT-30, 60, 30))
        pygame.draw.rect(screen, (80,80,80),
                         (config.SCREEN_WIDTH-58, config.SCREEN_HEIGHT-30, 60, 30), 3)
        fps_text = self.fonts.small_font.render(str(fps), True, (30,30,30))
        screen.blit(fps_text, (config.SCREEN_WIDTH-38, config.SCREEN_HEIGHT-23))

    def draw_hover_highlight(self, hovered_cell, screen, color=(255, 255, 255, 100)):
        """Draws a semi-transparent highlight over the hovered cell."""
        cell_y, cell_x = hovered_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - self.camera.x_pos) * config.CELL_SIZE  + config.SIDEBAR_WIDTH
        screen_y = (cell_y - self.camera.y_pos) * config.CELL_SIZE

        # Create transparent surface for the highlight
        highlight_surface = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(color)

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))

    def draw_selected_cell_border(self, selected_cell, screen, color=(255, 255, 0)):
        """Draws a border around the selected cell."""
        cell_y, cell_x = selected_cell

        # Convert grid cell to screen coordinates
        screen_x = (cell_x - self.camera.x_pos) * config.CELL_SIZE  + config.SIDEBAR_WIDTH
        screen_y = (cell_y - self.camera.y_pos) * config.CELL_SIZE

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
