import pygame
from utils import config

class EventHandler:
    def __init__(self, controller=None):
        self.controller = controller or None

        
    def handle_events(self, events, camera):
        """Main event handling loop."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.mouse_release_pos = pygame.mouse.get_pos()
                    if self.mouse_release_pos[0] > config.SIDEBAR_WIDTH and self.mouse_release_pos[0] < config.SCREEN_WIDTH:     #ensures mouse position is on the screen
                        r, c = self._get_cell_at_mouse_position(self.mouse_release_pos, camera)
                        self.controller.select_cell(r, c)
            
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


        mouse_pos = pygame.mouse.get_pos()
        r, c = self._get_cell_at_mouse_position(mouse_pos, camera)
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




    


    def _get_cell_at_mouse_position(self, pos, camera):
        mouse_x, mouse_y = pos
            
        # Convert screen coordinates to world coordinates
        world_x = (mouse_x - config.SIDEBAR_WIDTH) + (camera.x_pos * config.CELL_SIZE)
        world_y = mouse_y + (camera.y_pos * config.CELL_SIZE)

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        

        return cell_y, cell_x
