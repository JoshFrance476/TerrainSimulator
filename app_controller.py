import pygame
from utils import config

class AppController:
    def __init__(self, world, camera):
        self.world = world
        self.camera = camera

        self.active_left_sidebar = 0
        self.active_right_sidebar = 0

        self.selected_cell = None
        self.hovered_cell = None

        self.selected_filter = "None"
        self.magnified = False

        self.paused = True

        self.tick_count = 0


    
    def toggle_pause(self):
        self.paused = not self.paused

    def update(self):
        self.camera.clamp_pan()
        if not self.paused:
            self.world.step(self.tick_count)
            self.tick_count += 1
    
    def cycle_left_sidebar(self, delta):
        self.active_left_sidebar = (self.active_left_sidebar + delta) % 2

    def cycle_right_sidebar(self, delta):
        self.active_right_sidebar = (self.active_right_sidebar + delta) % 3
    
    def select_cell(self, r, c):
        self.selected_cell = (r, c)
    
    def hover_cell(self, r, c):
        self.hovered_cell = (r, c)
    
    def set_selected_filter(self, filter_name):
        self.selected_filter = filter_name


    def get_selected_cell(self):
        return self.selected_cell
    

    def pan_camera(self, dx, dy):
        self.camera.pan(dx, dy)
    
    def get_camera_position(self):
        return self.camera.x_pos, self.camera.y_pos
    
    def create_settlement(self, cell):
        self.world.create_settlement(cell[0], cell[1])

    def create_state(self, cell):
        self.world.create_state(cell[0], cell[1])

    def get_cell_at_mouse_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
            
        # Convert screen coordinates to world coordinates
        world_x = (mouse_x - config.SIDEBAR_WIDTH) + (self.camera.x_pos * config.CELL_SIZE)
        world_y = mouse_y + (self.camera.y_pos * config.CELL_SIZE)

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        return cell_y, cell_x


    def get_screen_data(self):
        return self.world.get_region_data(self.camera.x_pos, 
                                        self.camera.y_pos, 
                                        config.CAMERA_COLS+self.camera.x_pos, 
                                        config.CAMERA_ROWS+self.camera.y_pos)


    def get_magnifier_data(self):
        return self.world.get_region_data(self.hovered_cell[1]-config.MAGNIFIER_CELL_AMOUNT, 
                                        self.hovered_cell[0]-config.MAGNIFIER_CELL_AMOUNT, 
                                        self.hovered_cell[1]+config.MAGNIFIER_CELL_AMOUNT, 
                                        self.hovered_cell[0]+config.MAGNIFIER_CELL_AMOUNT)