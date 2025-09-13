import pygame
from utils.ui_utils import wrap_text

class InfoBoxList:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.info_boxes = []

    def add_info_box(self, info_box):
        self.info_boxes.append(info_box)

    def draw(self, screen):
        y_offset = self.y
        for box in self.info_boxes:
            box.draw(screen, self.x, y_offset, self.width)
            y_offset += box.height + 5

    def handle_event(self, event):
        for box in self.info_boxes:
            box.handle_event(event)


class InfoBox:
    TITLE_HEIGHT = 30
    PADDING = 10
    LINE_HEIGHT = 20

    def __init__(self, large_font, small_font, title="Untitled", visible_lines=None, hidden_lines=None):
        self.title = TextLink(title, None, large_font)
        self.visible_lines = visible_lines or {}
        self.hidden_lines = hidden_lines or {}
        self.large_font = large_font
        self.small_font = small_font
        self.height = self.TITLE_HEIGHT + len(self.visible_lines) * self.LINE_HEIGHT
        self.expanded = False

    def set_info(self, title, visible_lines, hidden_lines = None):
        self.title = TextLink(title, None, self.large_font)
        self.visible_lines = visible_lines
        self.hidden_lines = hidden_lines or {}
        self.update_height()
    
    def add_text_link_action(self, action):
        self.title.action = action

    def update_height(self):
        lines = len(self.visible_lines) + (len(self.hidden_lines) if self.expanded else 0)
        self.height = self.TITLE_HEIGHT + lines * self.LINE_HEIGHT

    def draw(self, screen, x, y, width):        
        lines = list(self.visible_lines.items())
        if self.expanded:
            lines += list(self.hidden_lines.items())

        max_text_width = width - self.PADDING*2

        all_wrapped_lines = []
        for label, value in lines:
            wrapped_lines = wrap_text(f"{label}: {value}", self.small_font, max_text_width)
            all_wrapped_lines.extend(wrapped_lines)

        self.height = self.TITLE_HEIGHT + len(all_wrapped_lines) * self.LINE_HEIGHT

        rect = pygame.Rect(x, y, width, self.height)
        pygame.draw.rect(screen, (220,220,220), rect)
        pygame.draw.rect(screen, (80,80,80), rect, 2)

        self.title.draw(screen, x + self.PADDING, y + 5)

        y_offset = y + self.TITLE_HEIGHT

        for line in all_wrapped_lines:
                text_surface = self.small_font.render(line, True, (30,30,30))
                screen.blit(text_surface, (x + self.PADDING, y_offset))
                y_offset += self.LINE_HEIGHT
            
        

    def handle_event(self, event):
        pass  # base InfoBox is passive


class CollapsibleInfoBox(InfoBox):
    def __init__(self, large_font, small_font):
        super().__init__(large_font, small_font)
        self.toggle_button = Button(
            0, 0, self.TITLE_HEIGHT-8, self.TITLE_HEIGHT-8,
            action=self.toggle_expanded,
            toggle=False
        )

    def toggle_expanded(self):
        self.expanded = not self.expanded
        self.update_height()

    def draw(self, screen, x, y, width):
        super().draw(screen, x, y, width)
        self.toggle_button.rect.topleft = (x + width - self.toggle_button.rect.width - 4, y + 4)
        self.toggle_button.draw(screen)

    def handle_event(self, event):
        self.toggle_button.handle_event(event)
        self.title.handle_event(event)


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

class TextLink:
    def __init__(self, text, action, font):
        self.text = text
        self.action = action
        self.font = font
        self.rect = None


    def draw(self, screen, x, y):
        text = self.font.render(self.text, True, (30, 30, 30))
        self.rect = pygame.Rect(x, y, 100, 20)

        screen.blit(text, (x, y))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()

