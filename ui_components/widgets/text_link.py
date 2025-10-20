import pygame
from utils.ui_utils import wrap_text

class TextLink:
    def __init__(self, text, action, font):
        self.text = text
        self.action = action
        self.font = font
        self.rect = None
        self.height = 0
        self.width = 0

    def draw(self, screen, x, y):
        y_offset = y

        for line in wrap_text(self.text, self.font, self.width):
            text = self.font.render(line, True, (30, 30, 30))
            screen.blit(text, (x, y_offset))
            y_offset += 20

        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def set_width(self, width):
        self.width = width

    def update_height(self):
        height = 0
        for line in wrap_text(self.text, self.font, self.width):
            height += 20
        self.height = height + 5

    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

