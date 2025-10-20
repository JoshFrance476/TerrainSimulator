import pygame

class Button:
    def __init__(self, x, y, width, height, action, label="", font=None, toggle=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.label = label
        self.font = font
        self.toggle = toggle
        self.toggled = False

    def draw(self, screen):
        mouse_over = self.rect.collidepoint(pygame.mouse.get_pos())

        if self.toggle and self.toggled:
            base_color = (150, 150, 220)  # toggled on
        elif mouse_over:
            base_color = (180, 180, 180)  # hover
        else:
            base_color = (220, 220, 220)  # normal

        pygame.draw.rect(screen, base_color, self.rect)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 2)

        if self.label and self.font:
            text = self.font.render(self.label, True, (30, 30, 30))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.toggle:
                    self.toggled = not self.toggled
                self.action()