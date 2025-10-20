import pygame

class InfoBoxList:
    SCROLL_SPEED = 20
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.info_boxes = []
        self.scroll_offset = 0

    def add_info_box(self, info_box):
        info_box.set_width(self.width)
        self.info_boxes.append(info_box)
    
    def reset(self):
        self.info_boxes.clear()

    def draw(self, screen):
        y_offset = self.y - self.scroll_offset
        clip_rect = pygame.Rect(0, self.y, self.width, pygame.display.get_surface().get_height() - self.y)
        screen.set_clip(clip_rect)

        for box in self.info_boxes:
            if y_offset + box.height < self.y:
                y_offset += box.height + 5
                continue
            if y_offset > clip_rect.bottom:
                break
            box.draw(screen, self.x, y_offset)
            y_offset += box.height + 5

        screen.set_clip(None)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            total_height = sum(box.height + 5 for box in self.info_boxes)
            visible_height = pygame.display.get_surface().get_height() - self.y
            max_scroll = max(0, total_height - visible_height)
            self.scroll_offset -= event.y * self.SCROLL_SPEED
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        else:
            for box in self.info_boxes:
                box.handle_event(event)