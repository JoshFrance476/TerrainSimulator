import pygame

class InfoBoxList:
    SCROLL_SPEED = 20
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.info_boxes = []
        self.scroll_offset = 0

    def add_info_box(self, info_box):
        info_box.set_width(self.width)
        self.info_boxes.append(info_box)
    
    def reset(self):
        self.info_boxes.clear()

    def draw(self, screen, x, y, parent_clip=None):
        y_offset = y - self.scroll_offset
        clip_rect = pygame.Rect(x, y, self.width, self.height)

        if parent_clip:
            clip_rect = clip_rect.clip(parent_clip)

        screen.set_clip(clip_rect)

        for box in self.info_boxes:
            if y_offset + box.height < y:
                y_offset += box.height + 5
                continue
            if y_offset > clip_rect.bottom:
                break
            box.draw(screen, x, y_offset, parent_clip=clip_rect)
            y_offset += box.height + 5

        screen.set_clip(parent_clip)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            total_height = sum(box.height + 5 for box in self.info_boxes)
            max_scroll = max(0, total_height - self.height)
            self.scroll_offset -= event.y * self.SCROLL_SPEED
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
            for box in self.info_boxes:
                if box.info_box_list:
                    box.info_box_list.handle_event(event)
        else:
            for box in self.info_boxes:
                box.handle_event(event)