import pygame

class Button:
    def __init__(self,width, height, action, label="", font=None):
        self.rect = None
        self.action = action
        self.label = label
        self.font = font
        self.width = width
        self.height = height
        self.left_padding = 10
        
        self.focused = False

    def draw(self, screen, x, y):
        self.rect = pygame.Rect(x, y, self.width, self.height)

        if self.focused:
            base_color = (150, 150, 220)  # toggled on
        elif self.collide_with(pygame.mouse.get_pos()):
            base_color = (180, 180, 180)  # hover
        else:
            base_color = (220, 220, 220)  # normal
  

        pygame.draw.rect(screen, base_color, self.rect)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 2)

        if self.label and self.font:
            text = self.font.render(self.label, True, (30, 30, 30))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)

    def is_clicked(self, event):
        self.action()
    
    def collide_with(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)