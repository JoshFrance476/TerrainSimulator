import pygame

class Label:
    def __init__(self, text, small_font):
        self.text = text
        self.small_font = small_font
    
    def draw(self, screen, x, y):
        text_surface = self.small_font.render(self.text, True, (30,30,30))
        screen.blit(text_surface, (x, y))