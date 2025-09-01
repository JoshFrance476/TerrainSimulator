import pygame
from utils import config

class EventHandler:
    def __init__(self):
        self.mouse_release_pos = None
        
        # Selection state
        self.selected_cell = None
        self.hovered_cell = None
        
        # Game state
        self.paused = True
        self.selected_filter = 0

        
    def handle_events(self, camera):
        """Main event handling loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._handle_quit()
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard(event, camera)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_release(event, camera)
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            camera.x_pos -= config.PAN_STEP
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            camera.x_pos += config.PAN_STEP
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            camera.y_pos -= config.PAN_STEP
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            camera.y_pos += config.PAN_STEP


        # Update hover state
        self._update_hover_state(camera)

    def _handle_quit(self):
        """Handle application quit."""
        pygame.quit()
        exit()

    def _handle_keyboard(self, event, camera):
        """Handle keyboard input."""
        if event.key == pygame.K_SPACE:
            self.paused = not self.paused
        elif event.key == pygame.K_0:
            self.selected_filter = 0
        elif event.key == pygame.K_1:
            self.selected_filter = 1
        elif event.key == pygame.K_2:
            self.selected_filter = 2
        elif event.key == pygame.K_3:
            self.selected_filter = 3
        elif event.key == pygame.K_4:
            self.selected_filter = 4
        elif event.key == pygame.K_5:
            self.selected_filter = 5
        elif event.key == pygame.K_6:
            self.selected_filter = 6
        elif event.key == pygame.K_7:
            self.selected_filter = 7
        elif event.key == pygame.K_8:
            self.selected_filter = 8



    def _handle_mouse_release(self, event, camera):
        """Handle mouse button release events."""
        if event.button == 1:  # Left mouse button
            self.mouse_release_pos = pygame.mouse.get_pos()
            if self.mouse_release_pos:     #ensures mouse position is on the screen
                self.selected_cell = self._get_cell_at_mouse_position(self.mouse_release_pos, camera)



    def _update_hover_state(self, camera):
        """Update the currently hovered cell."""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_cell = self._get_cell_at_mouse_position(mouse_pos, camera)


    def _get_cell_at_mouse_position(self, pos, camera):
        mouse_x, mouse_y = pos

        # Convert screen coordinates to world coordinates
        world_x = mouse_x + (camera.x_pos * config.CELL_SIZE)
        world_y = mouse_y + (camera.y_pos * config.CELL_SIZE)

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        return cell_y, cell_x
    
    def get_selected_filter(self):
        return self.selected_filter