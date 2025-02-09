from utils import config

class Camera:
    def __init__(self):
        self.zoom_level = 1.0
        self.x_offset, self.y_offset = 0, 0

    def zoom(self, amount, mouse_x, mouse_y):
        new_zoom = min(config.MAX_ZOOM, max(config.MIN_ZOOM, self.zoom_level + amount))
        if new_zoom != self.zoom_level:
            world_x_before = (mouse_x + self.x_offset) / self.zoom_level
            world_y_before = (mouse_y + self.y_offset) / self.zoom_level
            self.zoom_level = new_zoom
            self.x_offset = world_x_before * self.zoom_level - mouse_x
            self.y_offset = world_y_before * self.zoom_level - mouse_y

    def clamp_pan(self):
        max_x = max(0, config.COLS * config.CELL_SIZE * self.zoom_level - config.WIDTH)
        max_y = max(0, config.ROWS * config.CELL_SIZE * self.zoom_level - config.HEIGHT)
        self.x_offset = max(0, min(self.x_offset, max_x))
        self.y_offset = max(0, min(self.y_offset, max_y))
