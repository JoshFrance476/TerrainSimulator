import pygame
import config as config
from app.app_controller import AppController

pygame.init()

class FontManager:
    def __init__(self):
        self.header = pygame.font.SysFont("gill-sans", config.FONT_SIZE+3)
        self.large_font = pygame.font.SysFont("gill-sans", config.FONT_SIZE)
        self.small_font = pygame.font.SysFont("gill-sans", config.FONT_SIZE-3)


# Initialize screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH + config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("World Studio")

fonts = FontManager()


controller = AppController(screen, fonts)

clock = pygame.time.Clock()

tick_count = 0


while True:
    events = pygame.event.get()

    controller.tick(events)

    pygame.display.flip()
    clock.tick(config.TARGET_FPS)


