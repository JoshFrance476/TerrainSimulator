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
    def __init__(self, state, camera, story_engine, fonts, world, brush, player, generate_map_func, load_file_func, save_file_func):
        self.state = state
        self.camera = camera
        self.interaction_system = None
        self.story_engine = story_engine
        self.world = world
        self.fonts = fonts
        self.brush = brush
        self.player = player

        self._last_left_page = None

        self._current_brush_type = None

        self._last_selected_cell = None
        self._last_hovered_cell = None

        self.generate_map_func = generate_map_func
        self.load_file_func = load_file_func
        self.save_file_func = save_file_func

    def set_interaction_system(self, interaction_system):
        self.interaction_system = interaction_system
        self.left_sidebar = LeftSidebarController(self.fonts, self.state, self.world, self.interaction_system, self.story_engine)
        self.right_sidebar = RightSidebarController(self.fonts, self.story_engine, self.interaction_system)
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
        
        if self.state.update_right_page or self.story_engine.poll():
            self.right_sidebar.show_current_scenario_screen()
            self.state.update_right_page = False
        

        if selected_cell:
            self.draw_cell_border(selected_cell, screen, color=(255, 255, 0))
        
        self.draw_cell_border(self.player.get_location(), screen)

        self.left_sidebar.draw(screen)
        self.right_sidebar.draw(screen)

        if self.mouse_on_map():
            if hovered_cell:
                self.draw_hover_highlight(hovered_cell, screen)
            
            if self._last_hovered_cell != hovered_cell:
                self.tooltips.generate_tooltip_list(hovered_cell)
                self._last_hovered_cell = hovered_cell
            self.tooltips.draw(screen)

            if self.state.interaction_type in {InteractionType.PAINT_REGION, InteractionType.PAINT_TILE, InteractionType.EDIT_ELEVATION}:
                self.draw_brush_outline(screen)
        
        if self.state.show_menu:
            self.menu.draw(screen)
        
        if self.state.interaction_type in {InteractionType.PAINT_REGION, InteractionType.PAINT_TILE, InteractionType.EDIT_ELEVATION}:
            if self.state.interaction_type is not self._current_brush_type:
                self.brush_window.show_page(self.state.interaction_type)
                self._current_brush_type = self.state.interaction_type
                self.brush_window.set_attributes(self.brush.get_attributes())
            self.brush_window.draw(screen)

        if self.world.current_path:
            self.draw_path(self.world.current_path, screen)

        
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
        cs = self.camera.cell_size

        screen_x, screen_y = self.grid_to_screen((cell_x, cell_y))

        # Create transparent surface for the highlight
        highlight_surface = pygame.Surface((cs, cs), pygame.SRCALPHA)
        highlight_surface.fill(color)

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))
    
    def draw_path(self, path, screen):
        for x,y in path:
            self.draw_hover_highlight((y, x), screen)

    def draw_brush_outline(self, screen, color=(255, 255, 255, 180)):
        """Draws a grid-aligned outline around the tiles covered by the brush."""
        hovered_cell = self.state.hovered_cell
        if hovered_cell is None:
            return

        cs = self.camera.cell_size
        thickness = max(1, cs // 8)

        # Get the boolean mask of which world tiles the brush covers
        mask = self.brush.get_brush_mask(hovered_cell, boolean=True)

        # Only iterate over the visible camera region to avoid off-screen work
        x0, y0, x1, y1 = self.camera.get_boundaries()

        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)

        for world_y in range(max(0, y0), min(mask.shape[0], y1)):
            for world_x in range(max(0, x0), min(mask.shape[1], x1)):
                if not mask[world_y, world_x]:
                    continue

                sx, sy = self.grid_to_screen((world_x, world_y))

                # Draw a border edge wherever the neighbour is outside the brush mask
                if world_y == 0 or not mask[world_y - 1, world_x]:  # top edge
                    pygame.draw.line(overlay, color, (sx, sy), (sx + cs, sy), thickness)
                if world_y + 1 >= mask.shape[0] or not mask[world_y + 1, world_x]:  # bottom edge
                    pygame.draw.line(overlay, color, (sx, sy + cs), (sx + cs, sy + cs), thickness)
                if world_x == 0 or not mask[world_y, world_x - 1]:  # left edge
                    pygame.draw.line(overlay, color, (sx, sy), (sx, sy + cs), thickness)
                if world_x + 1 >= mask.shape[1] or not mask[world_y, world_x + 1]:  # right edge
                    pygame.draw.line(overlay, color, (sx + cs, sy), (sx + cs, sy + cs), thickness)

        screen.blit(overlay, (0, 0))

    def draw_cell_border(self, cell, screen, color=(255, 255, 255)):
        cell_y, cell_x = cell
        cs = self.camera.cell_size

        screen_x, screen_y = self.grid_to_screen((cell_x, cell_y))

        # Create transparent surface for the border
        highlight_surface = pygame.Surface((cs, cs), pygame.SRCALPHA)

        # Draw rectangle border with scaled thickness
        pygame.draw.rect(
            highlight_surface,
            color,
            (0, 0, cs, cs),
            max(1, cs // 8)  # Scale border thickness with zoom
        )

        # Blit highlight onto the screen
        screen.blit(highlight_surface, (screen_x, screen_y))
    
    def grid_to_screen(self, grid_location):
        return (grid_location[0] - self.camera.x_pos) * self.camera.cell_size + config.SIDEBAR_WIDTH, (grid_location[1] - self.camera.y_pos) * self.camera.cell_size