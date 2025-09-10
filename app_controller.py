class AppController:
    def __init__(self, world, event_handler, camera):
        self.world = world
        self.event_handler = event_handler
        self.camera = camera

        self.active_left_sidebar = 0
        self.active_right_sidebar = 0

        self.selected_cell = None
        self.hovered_cell = None

        self.selected_filter = "None"
        self.magnified = False

        self.paused = True

    
    def toggle_pause(self):
        self.paused = not self.paused

    def update(self):
        if not self.paused:
            self.world.step()
    
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
    
    def select_cell(self, r, c):
        self.selected_cell = (r, c)

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

    
