import pygame
from .. import config
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
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.controller.pan_camera(-config.PAN_STEP, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.controller.pan_camera(config.PAN_STEP, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.controller.pan_camera(0, -config.PAN_STEP)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.controller.pan_camera(0, config.PAN_STEP)
        
        self.controller.magnified = keys[pygame.K_LCTRL]


        r, c = self.controller.get_cell_at_mouse_position()
        self.controller.hover_cell(r, c)

    def _handle_keyboard(self, event):
        """Handle keyboard input."""
        if event.key == pygame.K_SPACE:
            self.controller.toggle_pause()
        elif event.key == pygame.K_0:
            self.controller.set_selected_filter("None")
        elif event.key == pygame.K_1:
            self.controller.set_selected_filter("Elevation")
        elif event.key == pygame.K_2:
            self.controller.set_selected_filter("Temperature")
        elif event.key == pygame.K_3:
            self.controller.set_selected_filter("Rainfall")
        elif event.key == pygame.K_4:
            self.controller.set_selected_filter("Population Capacity")
        elif event.key == pygame.K_5:
            self.controller.set_selected_filter("Fertility")
        elif event.key == pygame.K_6:
            self.controller.set_selected_filter("Traversal Cost")
        elif event.key == pygame.K_7:
            self.controller.set_selected_filter("Steepness")
        elif event.key == pygame.K_8:
            self.controller.set_selected_filter("Population")
        elif event.key == pygame.K_9:
            self.controller.set_selected_filter("Resource")
        elif event.key == pygame.K_p:
            self.controller.set_selected_filter("State")
        elif event.key == pygame.K_q:
            self.controller.cycle_right_sidebar(-1)
        elif event.key == pygame.K_e:
            self.controller.cycle_right_sidebar(1)
        elif event.key == pygame.K_z:
            self.controller.cycle_left_sidebar(-1)
        elif event.key == pygame.K_x:
            self.controller.cycle_left_sidebar(1)
        elif event.key == pygame.K_o:
            self.controller.generate_event("random event", self.controller.get_selected_cell())
