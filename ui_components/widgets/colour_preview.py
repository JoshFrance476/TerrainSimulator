import pygame
from utils.colour_utils import hsv2rgb

class ColourPreview:
    def __init__(self, width, height, h, s, v):
        self.width = width
        self.height = height
        self.h_slider, self.s_slider, self.v_slider = h, s, v

        self.left_padding = 5
    
    def draw(self, screen, x, y):
        rgb_colour = hsv2rgb(self.h_slider.value/360, self.s_slider.value/100, self.v_slider.value/100)
        pygame.draw.rect(screen, (0,0,0), (x, y, self.width, self.height))
        pygame.draw.rect(screen, rgb_colour, (x+2, y+2, self.width-4, self.height-4))


    
