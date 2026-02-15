import pygame
from utils.colour_utils import hsv2rgb

class ColourPreview:
    """
    Accepts HSV colours in the format h[0-360], s[0-1], v[0-1]
    """
    def __init__(self, width, height, h, s, v):
        self.width = width
        self.height = height
        self.left_padding = 5

        self.h_src = h
        self.s_src = s
        self.v_src = v

    @staticmethod
    def _get(src, normalised = False):
        # Slider-like object
        if hasattr(src, "value"):
            if normalised:
                return float(src.get_normalised_value())
            else:
                return float(src.value)
        # Callable
        if callable(src):
            return float(src())
        # Raw value
        return float(src)
    

    def draw(self, screen, x, y):
        h = self._get(self.h_src)
        s = self._get(self.s_src, True)
        v = self._get(self.v_src, True)

        r, g, b = hsv2rgb(h, s, v)
        


        pygame.draw.rect(screen, (0, 0, 0), (x, y, self.width, self.height))
        pygame.draw.rect(screen, (r, g ,b), (x + 2, y + 2, self.width - 4, self.height - 4))