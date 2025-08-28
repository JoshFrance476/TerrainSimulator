from utils import config

class Camera:
    def __init__(self):
        self.x_pos, self.y_pos = 0, 0  #Top-left corner of the camera view, in cell coordinates

    # Ensure camera does not pan beyond world boundaries
    def clamp_pan(self):
        max_x = config.WORLD_COLS - config.CAMERA_COLS #Find furthest x and y values the camera can go to without going out of bounds
        max_y = config.WORLD_ROWS - config.CAMERA_ROWS
        self.x_pos = max(0, min(self.x_pos, max_x))
        self.y_pos = max(0, min(self.y_pos, max_y))
