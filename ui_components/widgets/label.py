from utils.ui_utils import wrap_text

class Label:
    def __init__(self, text, font, max_width):
        self.text = text
        self.font = font
        self.max_width = max_width
        self.width = 0
        self.wrapped_text = wrap_text(self.text, font, max_width)
        self.height = 25 + (15 * max(0,(len(self.wrapped_text)-1)))

        for line in self.wrapped_text:
            if self.width < font.size(line)[0]:
                self.width = font.size(line)[0]
    
    def draw(self, screen, x, y):
        y_offset = y

        for line in self.wrapped_text:
            text_surface = self.font.render(line, True, (30,30,30))
            screen.blit(text_surface, (x, y_offset))
            y_offset += 15
