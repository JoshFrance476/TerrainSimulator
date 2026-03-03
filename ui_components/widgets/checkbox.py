import pygame

class Checkbox:
    def __init__(self, width, height, action, left_padding = 5, top_padding = 0):
        self.width = width
        self.height = height
        self.rect = None
        self.active = False
        self.top_padding = top_padding
        self.left_padding = left_padding
        self.action = action
    
    def draw(self, screen, x, y):
        self.rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(screen, (220, 220, 220), self.rect)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 2)


        if self.active:
            pygame.draw.rect(screen, (80, 80, 80), self.rect.inflate(-8, -8))
    
    def is_clicked(self, event):
        self.active = not self.active
        self.action(self.active)
    
    def collide_with(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)