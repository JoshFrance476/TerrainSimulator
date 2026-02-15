import pygame

class Slider:
    def __init__(self, font, min_val, max_val, bar_width, default_value = -1, left_padding = 5, top_padding = 0):
        self.min = min_val
        self.max = max_val
        self.bar_width = bar_width
        self.height = 15 + top_padding
        self.left_padding = left_padding
        self.top_padding = top_padding
        self.font = font
        self.bar_x_offset = 60

        if default_value >= min_val and default_value <= max_val:
            self.value = default_value
        else:
            self.value = min_val

        self.dragging = False
        self.focused = False

        self.bar_rect = None
        self.pin_rect = None

    def draw(self, screen, x, y):
        self.bar_rect = pygame.Rect(x+self.bar_x_offset+self.left_padding, y+self.top_padding, self.bar_width, self.height)

        # value → pixel
        t = (self.value - self.min) / (self.max - self.min)
        pin_x = x +self.left_padding + t * self.bar_width

        self.pin_rect = pygame.Rect(pin_x +self.left_padding + self.bar_x_offset-10, y+self.height/4+self.top_padding - 5, 20, 20)

        pygame.draw.rect(screen, (0, 0, 0), self.bar_rect, 2)
        pygame.draw.rect(screen, (0, 0, 0), self.pin_rect)

        value_text = self.font.render(str(self.value), True, (30,30,30))
        screen.blit(value_text, (x+self.left_padding, y+self.top_padding-3))

        min_text = self.font.render(str(self.min), True, (30,30,30))
        screen.blit(min_text, (x+self.left_padding+self.bar_x_offset-20, y+self.top_padding-3))

        max_text = self.font.render(str(self.max), True, (30,30,30))
        screen.blit(max_text, (x+self.left_padding+self.bar_width+self.bar_x_offset+10, y+self.top_padding-3))

    def collide_with(self, mouse_pos):
        return self.bar_rect and self.bar_rect.collidepoint(mouse_pos)

    def update_value(self, mouse_x):
        if not self.bar_rect:
            return

        # clamp mouse position
        mouse_x = max(self.bar_rect.left,
                      min(mouse_x, self.bar_rect.right))

        # pixel → value
        t = (mouse_x - self.bar_rect.left) / self.bar_width
        self.value = int(self.min + t * (self.max - self.min))

    def is_clicked(self, event):
        self.dragging = True
        self.update_value(event.pos[0])
        
    
    def is_dragged(self, event):
        if self.dragging:
            self.update_value(event.pos[0])

    def stop_drag(self):
        self.dragging = False
    
    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1
    
    def get_normalised_value(self):
        return self.value/(self.max-self.min)

    