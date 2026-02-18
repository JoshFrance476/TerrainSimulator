import pygame
from utils.ui_utils import wrap_text

class Button:
    def __init__(self,width, height, action, label, font, left_padding = 5, top_padding = 0):
        self.rect = None
        self.action = action
        self.label = label
        self.font = font
        self.width = width
        self.wrapped_text = wrap_text(self.label, font, self.width)
        self.height = height + (15 * max(0,(len(self.wrapped_text)-1)))
        self.left_padding = left_padding
        self.top_padding = top_padding
        
        self.focused = False

    def draw(self, screen, x, y):
        self.rect = pygame.Rect(x+self.left_padding, y+self.top_padding, self.width, self.height)

        if self.focused:
            base_color = (150, 150, 220)  # toggled on
        elif self.collide_with(pygame.mouse.get_pos()):
            base_color = (180, 180, 180)  # hover
        else:
            base_color = (220, 220, 220)  # normal
  

        pygame.draw.rect(screen, base_color, self.rect)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 2)

        if self.label and self.font:
            y_offset = y

            for line in self.wrapped_text:
                text_surface = self.font.render(line, True, (30,30,30))
                screen.blit(text_surface, (x+self.left_padding, y_offset+self.top_padding))
                y_offset += 15


    def is_clicked(self, event):
        self.action()
    
    def collide_with(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)