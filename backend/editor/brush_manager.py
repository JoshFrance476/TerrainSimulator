import numpy as np
import config as config

class BrushManager:
    def __init__(self):
        self.size = 6
        self.strength = 0.02
    

    def get_brush_mask(self, location, boolean=True, negative=False):
        y0, x0 = location

        yy, xx = np.ogrid[:config.WORLD_ROWS, :config.WORLD_COLS]

        dist = np.sqrt((xx - x0)**2 + (yy - y0)**2)

        mask = 1 - (dist / self.size) 
        mask = np.clip(mask, 0, 1)

        if boolean:
            return mask > 0
        else:
            if negative:
                return mask * (-self.strength)
            else:
                return mask * self.strength
    
    def get_attributes(self):
        return {
            "size": self.size,
            "strength": self.strength
        }
    
    
