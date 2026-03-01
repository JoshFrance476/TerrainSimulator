import config

class Camera:
    def __init__(self):
        self.x_pos, self.y_pos = 0, 0  #Top-left corner of the camera view, in cell coordinates

    # Ensure camera does not pan beyond world boundaries
    def clamp_pan(self):
        max_x = config.WORLD_COLS - config.CAMERA_COLS #Find furthest x and y values the camera can go to without going out of bounds
        max_y = config.WORLD_ROWS - config.CAMERA_ROWS
        self.x_pos = max(0, min(self.x_pos, max_x))
        self.y_pos = max(0, min(self.y_pos, max_y))

    def pan(self, dx, dy):
        self.x_pos += dx
        self.y_pos += dy

    def set_location(self, location):
        self.x_pos, self.y_pos = int(location[1]-config.CAMERA_COLS/2)+1, int(location[0]-config.CAMERA_ROWS/2)+1   #The extra '+1' are to compensate for rounding down in odd division
    
    def get_position(self):
        return self.x_pos, self.y_pos

    def get_boundaries(self):
        return self.x_pos, self.y_pos, config.CAMERA_COLS+self.x_pos, config.CAMERA_ROWS+self.y_pos
    