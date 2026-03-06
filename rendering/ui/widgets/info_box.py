import pygame
from ui_components.widgets.text_link import TextLink
from ui_components.widgets.info_box_list import InfoBoxList
from rendering.ui.text_utils import wrap_text

class InfoBox:
    PADDING = 10
    LINE_HEIGHT = 20

    def __init__(self, large_font, small_font, title="Untitled", visible_lines=None, hidden_lines=None):
        self.title = TextLink(title, None, large_font)
        self.visible_lines = visible_lines or {}
        self.hidden_lines = hidden_lines or {}
        self.large_font = large_font
        self.small_font = small_font
        self.height = 0
        self.expanded = False
        self.width = 0
        self.wrapped_lines = []
        self.info_box_list = None

    def set_info(self, title, visible_lines, hidden_lines = None):
        self.title.text = title
        self.visible_lines = visible_lines
        self.hidden_lines = hidden_lines or {}
        self.update_height()
    
    def update_info_box_list(self, info_boxes):
        for info_box in info_boxes:
            self.info_box_list.add_info_box(info_box)
    
    def add_text_link_action(self, action):
        self.title.action = action
    
    def set_width(self, width):
        self.width = width
        self.title.set_width(self.width - self.PADDING)

    def update_height(self):
        lines = list(self.visible_lines.items())
        if self.expanded:
            lines += list(self.hidden_lines.items())
        
        self.title.update_height()

        max_text_width = self.width - self.PADDING*2

        all_wrapped_lines = []
        for label, value in lines:
            wrapped_lines = wrap_text(f"{label}: {value}", self.small_font, max_text_width)
            all_wrapped_lines.extend(wrapped_lines)
        
        self.height = len(all_wrapped_lines) * self.LINE_HEIGHT + self.title.height
        self.wrapped_lines = all_wrapped_lines

        if self.info_box_list:
            self.height += self.info_box_list.height



    def draw(self, screen, x, y, parent_clip=None):        
        self.update_height()

        rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(screen, (220,220,220), rect)
        pygame.draw.rect(screen, (80,80,80), rect, 2)

        self.title.draw(screen, x + self.PADDING, y + 5)

        y_offset = y + self.title.height

        for line in self.wrapped_lines:
                text_surface = self.small_font.render(line, True, (30,30,30))
                screen.blit(text_surface, (x + self.PADDING, y_offset))
                y_offset += self.LINE_HEIGHT
        
        if self.info_box_list:
            self.info_box_list.draw(screen, x+5, y_offset, parent_clip)
            
        

    def handle_event(self, event):
        pass  # base InfoBox is passive