import pygame

class LineDivider:
    def __init__(self, width, thickness=2, side_padding = 10, top_padding = 0, bottom_padding = 0):
        self.width = width
        self.left_padding = side_padding
        self.thickness = thickness
        self.top_padding = top_padding
        self.bottom_padding = bottom_padding
        self.height = self.top_padding + self.bottom_padding
    
    def draw(self, screen, x, y):
        pygame.draw.line(screen, (0,0,0), (x, y+self.top_padding), (x+self.width-self.left_padding*2, y+self.top_padding), self.thickness)