import config

# Zoom levels as discrete cell sizes (pixels per cell)
ZOOM_LEVELS = [4, 6, 8, 12, 16, 24, 32]
DEFAULT_ZOOM_INDEX = ZOOM_LEVELS.index(config.CELL_SIZE) if config.CELL_SIZE in ZOOM_LEVELS else len(ZOOM_LEVELS) // 2

class Camera:
    def __init__(self):
        self.x_pos, self.y_pos = 0, 0  #Top-left corner of the camera view, in cell coordinates
        self._zoom_index = DEFAULT_ZOOM_INDEX

    @property
    def cell_size(self):
        """Current pixel size of each world cell, reflecting zoom level."""
        return ZOOM_LEVELS[self._zoom_index]

    @property
    def visible_cols(self):
        """How many world columns fit in the viewport at the current zoom."""
        map_pixel_width = config.SCREEN_WIDTH - config.SIDEBAR_WIDTH
        return map_pixel_width // self.cell_size

    @property
    def visible_rows(self):
        """How many world rows fit in the viewport at the current zoom."""
        return config.SCREEN_HEIGHT // self.cell_size

    def zoom(self, direction, mouse_world_col=None, mouse_world_row=None):
        """Zoom in (direction > 0) or out (direction < 0), keeping the cell
        under the mouse pointer stationary when mouse world coords are given."""
        old_cell_size = self.cell_size

        new_index = self._zoom_index + (1 if direction > 0 else -1)
        self._zoom_index = max(0, min(len(ZOOM_LEVELS) - 1, new_index))

        # Re-centre on the hovered cell so the view feels anchored there
        if mouse_world_col is not None and mouse_world_row is not None:
            map_pixel_width = config.SCREEN_WIDTH - config.SIDEBAR_WIDTH
            # Fraction of viewport the mouse was at before zoom
            frac_x = (mouse_world_col - self.x_pos) / (map_pixel_width / old_cell_size)
            frac_y = (mouse_world_row - self.y_pos) / (config.SCREEN_HEIGHT / old_cell_size)
            # Shift camera so that fraction stays the same after zoom
            self.x_pos = int(mouse_world_col - frac_x * self.visible_cols)
            self.y_pos = int(mouse_world_row - frac_y * self.visible_rows)

        self.clamp_pan()

    # Ensure camera does not pan beyond world boundaries
    def clamp_pan(self):
        max_x = max(0, config.WORLD_COLS - self.visible_cols)
        max_y = max(0, config.WORLD_ROWS - self.visible_rows)
        self.x_pos = max(0, min(self.x_pos, max_x))
        self.y_pos = max(0, min(self.y_pos, max_y))

    def pan(self, dx, dy):
        self.x_pos += dx
        self.y_pos += dy
        self.clamp_pan()

    def set_location(self, location):
        self.x_pos = int(location[1] - self.visible_cols / 2) + 1
        self.y_pos = int(location[0] - self.visible_rows / 2) + 1
    
    def get_position(self):
        return self.x_pos, self.y_pos

    def get_boundaries(self):
        return self.x_pos, self.y_pos, self.visible_cols + self.x_pos, self.visible_rows + self.y_pos