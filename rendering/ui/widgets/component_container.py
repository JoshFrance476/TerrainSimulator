import pygame

class ComponentContainer:
    def __init__(self, border = False):
        self.components = []
        self.height = 0
        self.border = border
        self.width = 0
    
    def add_component(self, component):
        self.components.append(component)
        if isinstance(component, list):
            self.height += component[0].height
        else:
            self.height += component.height

    def set_width(self, width):
        self.width = width
    
    
    def draw(self, screen, x, y, clip_rect):

        screen.set_clip(clip_rect)

        if self.border:
            pygame.draw.rect(screen, (80, 80, 80), (x, y, self.width, self.height))
            pygame.draw.rect(screen, (220, 220, 220), (x+2, y+2, self.width-4, self.height-4))
        y_offset = 0
        for component in self.components:
            if isinstance(component, list):
                x_offset = x
                for subcomponent in component:
                    subcomponent.draw(screen, subcomponent.left_padding+x_offset, y+y_offset)
                    x_offset += subcomponent.width+subcomponent.left_padding
            else:
                component.draw(screen, x+component.left_padding, y+y_offset)
                y_offset += component.height
        
        screen.set_clip(None)