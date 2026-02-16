import pygame

class Tooltip:
    def __init__(self, controller, font):
        self.components = []
        self.controller = controller
        self.font = font
        self.width = 0
        self.max_width = 200
        self.height = 0
    
    def add_components(self, component_list):
        self.components.extend(component_list)
        self.update_size()
        
    def update_size(self):
        height = 0
        width = 0
        for component in self.components:
            height += component.height
            if component.width > width:
                width = component.width
        self.height = height
        self.width = width
    
    def draw(self, screen, x, y):
        pygame.draw.rect(screen, (220,220,220),
                         (x, y, self.width+10, self.height+5))
        pygame.draw.rect(screen, (80,80,80),
                         (x, y, self.width+10, self.height+5), 3)
        
        y_offset = y
        for component in self.components:
            component.draw(screen, x+5, y_offset+5)
            y_offset += component.height