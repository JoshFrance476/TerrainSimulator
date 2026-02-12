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
        self.mouse_release_pos = pygame.mouse.get_pos()
        if self.mouse_release_pos[0] > config.SIDEBAR_WIDTH and self.mouse_release_pos[0] < config.SCREEN_WIDTH:     #ensures mouse position is on the screen
            r, c = self.controller.get_cell_at_mouse_position()
            if event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.controller.interaction_type == "paint_region":
                        self.controller.create_new_region((r, c))
                    else:
                        self.controller.interact_with_tile(r, c)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    if self.controller.interaction_type == "paint_region":
                        self.controller.active_region_paint = None
                        self.controller.interact_with_tile(r, c)
        
    
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

        if not self.controller.matches_hovered_tile((r, c)):
            self.controller.new_hovered_tile((r, c))

    def _handle_keyboard(self, event):
        """Handle keyboard input."""
        if self.controller.selected_textbox:
            self.controller.selected_textbox.handle_text_input(event)
        else:
            if event.key == pygame.K_SPACE:
                self.controller.toggle_pause()
            if event.key == pygame.K_m:
                self.controller.toggle_move()
            if event.key == pygame.K_n:
                self.controller.toggle_region_place()
            if event.key == pygame.K_b:
                self.controller.toggle_view_tile()
            if event.key == pygame.K_z:
                print("Debug Trigger")