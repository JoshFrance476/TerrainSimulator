import numpy as np
import config

class BrushManager:
    def __init__(self):
        self.brush_size = 5
        self.brush_strength = 0.02
    
    def get_brush(self, location):
        brush_locations = []
        for x in range(self.brush_size):
            for y in range(self.brush_size):
                brush_locations.append((location[0] + (1 - x), location[1] + (1 - y)))
        return brush_locations

    def get_brush_mask(self, location, max_strength, boolean=False):
        y0, x0 = location

        yy, xx = np.ogrid[:config.WORLD_ROWS, :config.WORLD_COLS]

        dist = np.sqrt((xx - x0)**2 + (yy - y0)**2)

        mask = 1 - (dist / self.brush_size)
        mask = np.clip(mask, 0, 1)

        if boolean:
            return mask > 0
        else:
            return mask * max_strength
    
    
