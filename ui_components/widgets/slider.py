import pygame

class Slider:
    def __init__(self, min_val, max_val, width):
        self.min = min_val
        self.max = max_val
        self.width = width
        self.height = 10
        self.value = min_val
        self.padding = 30

        self.focused = False

        self.bar_rect = None
        self.pin_rect = None

    def draw(self, screen, x, y):
        self.bar_rect = pygame.Rect(x, y, self.width, self.height)

        # value → pixel
        t = (self.value - self.min) / (self.max - self.min)
        pin_x = x + t * self.width

        self.pin_rect = pygame.Rect(pin_x - 10, y - 5, 20, 20)

        pygame.draw.rect(screen, (0, 0, 0), self.bar_rect, 2)
        pygame.draw.rect(screen, (0, 0, 0), self.pin_rect)

    def collide_with(self, mouse_pos):
        return self.bar_rect and self.bar_rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        mouse_x = event.pos[0]
        if not self.bar_rect:
            return

        # clamp mouse position
        mouse_x = max(self.bar_rect.left,
                      min(mouse_x, self.bar_rect.right))

        # pixel → value
        t = (mouse_x - self.bar_rect.left) / self.width
        self.value = int(self.min + t * (self.max - self.min))
        print(self.value)
    
    def is_dragged(self, event):
        self.is_clicked(event)
