import pygame
from utils.ui_utils import wrap_text

class Button:
    def __init__(self,width, height, action, label="", font=None, left_padding = 5, top_padding = 0):
        self.rect = None
        self.action = action
        self.label = label
        self.font = font
        self.width = width
        if font:
            self.wrapped_text = wrap_text(self.label, font, self.width)
            self.height = height + (2 * max(0,(len(self.wrapped_text)-2)))
        else:
            self.height = height
        self.left_padding = left_padding
        self.top_padding = top_padding
        
        self.focused = False

    def draw(self, screen, x, y):
        self.rect = pygame.Rect(
            x + self.left_padding,
            y + self.top_padding,
            self.width,
            self.height
        )

        if self.focused:
            base_color = (150, 150, 220)
        elif self.collide_with(pygame.mouse.get_pos()):
            base_color = (180, 180, 180)
        else:
            base_color = (220, 220, 220)

        pygame.draw.rect(screen, base_color, self.rect)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 2)

        if self.label and self.font:
            line_height = self.font.get_height()
            total_text_height = line_height * len(self.wrapped_text)

            # Vertical centering start position
            start_y = self.rect.y + (self.rect.height - total_text_height) // 2

            for i, line in enumerate(self.wrapped_text):
                text_surface = self.font.render(line, True, (30, 30, 30))
                text_rect = text_surface.get_rect()

                # Horizontal centering
                text_rect.centerx = self.rect.centerx

                # Vertical positioning
                text_rect.y = start_y + i * line_height

                screen.blit(text_surface, text_rect)



    def is_clicked(self, event):
        self.action()
    
    def collide_with(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)