from rendering.ui.text_utils import wrap_text
from config import SIDEBAR_WIDTH

class Label:
    def __init__(self, text, font, max_width=SIDEBAR_WIDTH, left_padding = 5, top_padding = 0):
        self.text = text
        self.font = font
        self.max_width = max_width
        self.width = 0
        self.wrapped_text = wrap_text(self.text, font, max_width)
        self.height = 25 + (15 * max(0,(len(self.wrapped_text)-1)))
        self.left_padding = left_padding
        self.top_padding = top_padding

        for line in self.wrapped_text:
            if self.width < font.size(line)[0]:
                self.width = font.size(line)[0]
    
    def draw(self, screen, x, y):
        y_offset = y

        for line in self.wrapped_text:
            text_surface = self.font.render(line, True, (30,30,30))
            screen.blit(text_surface, (x+self.left_padding, y_offset+self.top_padding))
            y_offset += 15
