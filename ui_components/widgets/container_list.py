import pygame
from config import SCROLL_SPEED

class ContainerList:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.containers = []
        self.left_padding = 5
        self.scroll_offset = 0

        self.container_combined_height = 0

        self.scroll_speed = SCROLL_SPEED

        self.focused = False
    
    def add_container(self, container):
        self.containers.append(container)
        container.set_width(self.width)
        self.container_combined_height += container.height
    
    
    def draw(self, screen, x, y):
        clip_rect = pygame.Rect(x, y, self.width, self.height)

        y += self.scroll_offset

        y_offset = 0
        for container in self.containers:
            container.draw(screen, x, y+y_offset, clip_rect)
            y_offset += container.height
    
    def scroll(self, scroll_y):
        self.scroll_offset += scroll_y * self.scroll_speed

        if self.scroll_offset > 0:
            self.scroll_offset = 0

        if self.scroll_offset < -self.container_combined_height + self.height:
            self.scroll_offset = -self.container_combined_height + self.height