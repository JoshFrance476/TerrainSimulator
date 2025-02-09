import pygame
from utils import config

class EventHandler:
    def __init__(self):
        # Mouse state
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_threshold = 5
        self.mouse_down_pos = None
        
        # Selection state
        self.selected_cell = None
        self.hovered_cell = None
        
        # Game state
        self.paused = False

    def handle_events(self, camera):
        """Main event handling loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._handle_quit()
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard(event, camera)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event, camera)
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event, camera)
            elif event.type == pygame.MOUSEWHEEL:
                self._handle_mouse_wheel(event, camera)

        # Update hover state
        self._update_hover_state(camera)

    def _handle_quit(self):
        """Handle application quit."""
        pygame.quit()
        exit()

    def _handle_keyboard(self, event, camera):
        """Handle keyboard input."""
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
            self._handle_keyboard_pan(event, camera)
        elif event.key == pygame.K_SPACE:
            self.paused = not self.paused

    def _handle_keyboard_pan(self, event, camera):
        """Handle keyboard-based camera panning."""
        if event.key == pygame.K_LEFT:
            camera.x_offset -= config.PAN_STEP
        elif event.key == pygame.K_RIGHT:
            camera.x_offset += config.PAN_STEP
        elif event.key == pygame.K_UP:
            camera.y_offset -= config.PAN_STEP
        elif event.key == pygame.K_DOWN:
            camera.y_offset += config.PAN_STEP

    def _handle_mouse_down(self, event):
        """Handle mouse button down events."""
        if event.button == 1:  # Left mouse button
            self.mouse_down_pos = pygame.mouse.get_pos()
            self.drag_start_x, self.drag_start_y = self.mouse_down_pos

    def _handle_mouse_up(self, event, camera):
        """Handle mouse button up events."""
        if event.button == 1:  # Left mouse button
            if self.mouse_down_pos and not self.dragging:
                self._handle_cell_selection(camera)
            self.dragging = False
            self.mouse_down_pos = None

    def _handle_mouse_motion(self, event, camera):
        """Handle mouse motion events."""
        if not self.mouse_down_pos:
            return

        current_pos = pygame.mouse.get_pos()
        dx = current_pos[0] - self.mouse_down_pos[0]
        dy = current_pos[1] - self.mouse_down_pos[1]
        
        # Check for drag threshold
        if not self.dragging and (dx * dx + dy * dy) > self.drag_threshold * self.drag_threshold:
            self.dragging = True
        
        # Handle drag movement
        if self.dragging:
            self._handle_drag_movement(current_pos, camera)

    def _handle_drag_movement(self, current_pos, camera):
        """Handle camera movement during drag."""
        current_x, current_y = current_pos
        dx = current_x - self.drag_start_x
        dy = current_y - self.drag_start_y
        camera.x_offset -= dx
        camera.y_offset -= dy
        self.drag_start_x, self.drag_start_y = current_x, current_y

    def _handle_mouse_wheel(self, event, camera):
        """Handle mouse wheel events for zooming."""
        camera.zoom(config.ZOOM_STEP * event.y, *pygame.mouse.get_pos())

    def _handle_cell_selection(self, camera):
        """Handle cell selection on click."""
        mouse_pos = pygame.mouse.get_pos()
        self.selected_cell = self._get_cell_at_mouse_position(
            *mouse_pos,
            camera.zoom_level,
            camera.x_offset,
            camera.y_offset
        )

    def _update_hover_state(self, camera):
        """Update the currently hovered cell."""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_cell = self._get_cell_at_mouse_position(
            *mouse_pos,
            camera.zoom_level,
            camera.x_offset,
            camera.y_offset
        )

    def _get_cell_at_mouse_position(self, mouse_x, mouse_y, zoom_level, x_offset, y_offset):
        """Convert screen coordinates to grid cell coordinates."""
        # Convert screen coordinates to world coordinates
        world_x = (mouse_x + x_offset) / zoom_level
        world_y = (mouse_y + y_offset) / zoom_level

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        return cell_y, cell_x