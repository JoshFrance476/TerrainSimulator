import pygame

class LineDivider:
    def __init__(self, width, thickness=2):
        self.width = width
        self.left_padding = 10
        self.height = 5
        self.thickness = thickness
    
    def draw(self, screen, x, y):
        pygame.draw.line(screen, (0,0,0), (x, y), (x+self.width, y), self.thickness)