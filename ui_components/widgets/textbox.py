from utils.ui_utils import wrap_text
import pygame

class TextBox:
    def __init__(self, controller, small_font, width, height):
        self.text = ""
        self.wrapped_text = []
        self.small_font = small_font
        self.width = width
        self.height = height
        self.controller = controller
        self.focused = False
        self.rect = None
        self.padding = 10
    
    def handle_event(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]

        elif event.key == pygame.K_RETURN:
            self.controller.clear_focus()

        elif event.unicode:
            self.text += event.unicode
        self.wrapped_text = wrap_text(self.text, self.small_font, self.width-5)
        self.height = 25 + (15 * max(0,(len(self.wrapped_text)-1)))

    def collide_with(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    
    def draw(self, screen, x, y):
        self.rect = pygame.Rect(x, y, self.width, self.height)
        border_color = (0, 120, 215) if self.focused else (80, 80, 80)
        pygame.draw.rect(screen, (220,220,220), self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)

        y_offset = y + 5

        for line in self.wrapped_text:
            text_surface = self.small_font.render(line, True, (30,30,30))
            screen.blit(text_surface, (x + 5, y_offset))
            y_offset += 15
