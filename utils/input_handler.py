import pygame
import config
import sys
class InputHandler:
    def __init__(self, controller):
        self.controller = controller

        
    def handle_event(self, event):
        """Main event handling loop."""
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            self._handle_keyboard(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.mouse_release_pos = pygame.mouse.get_pos()
                if self.mouse_release_pos[0] > config.SIDEBAR_WIDTH and self.mouse_release_pos[0] < config.SCREEN_WIDTH:     #ensures mouse position is on the screen
                    r, c = self.controller.get_cell_at_mouse_position()
                    self.controller.select_cell(r, c)
        
    
    def handle_continuous_inputs(self):
        if not self.controller.selected_textbox:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.controller.pan_camera(-config.PAN_STEP, 0)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.controller.pan_camera(config.PAN_STEP, 0)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.controller.pan_camera(0, -config.PAN_STEP)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.controller.pan_camera(0, config.PAN_STEP)


        r, c = self.controller.get_cell_at_mouse_position()
        self.controller.hover_cell(r, c)

    def _handle_keyboard(self, event):
        """Handle keyboard input."""
        if self.controller.selected_textbox:
            self.controller.selected_textbox.handle_text_input(event)
        else:
            if event.key == pygame.K_SPACE:
                self.controller.toggle_pause()
