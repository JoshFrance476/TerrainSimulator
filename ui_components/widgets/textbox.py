from utils.ui_utils import wrap_text
import pygame

class TextBox:
    def __init__(self, controller, small_font, x, y, width, height):
        self.text = ""
        self.wrapped_text = []
        self.small_font = small_font
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.controller = controller
        self.selected = False
        self.rect = None
    
    def handle_text_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_RETURN:
            self.controller.generate_event('user_event', self.controller.get_selected_cell(), self.text)
            self.text = ""
            self.wrapped_text = []
        elif event.unicode:
            self.text += event.unicode
        self.wrapped_text = wrap_text(self.text, self.small_font, self.width-5)
        self.height = 25 + (15 * max(0,(len(self.wrapped_text)-1)))

    def handle_mouse_input(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if not self.selected:
                    self.controller.select_textbox(self)
                    self.selected = True
            else:
                self.controller.select_textbox(None)
                self.selected = False
    
    def draw(self, screen):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        border_color = (0, 120, 215) if self.selected else (80, 80, 80)
        pygame.draw.rect(screen, (220,220,220), self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)

        y_offset = self.y + 5

        for line in self.wrapped_text:
            text_surface = self.small_font.render(line, True, (30,30,30))
            screen.blit(text_surface, (self.x + 5, y_offset))
            y_offset += 15
