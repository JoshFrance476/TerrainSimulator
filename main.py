import pygame
import config as config
from app_controller import AppController

#import tracemalloc
#tracemalloc.start()

pygame.init()

class FontManager:
    def __init__(self):
        self.large_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)
        self.small_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE-3)



# Initialize screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH + config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Terrain Generation")

fonts = FontManager()

controller = AppController(screen, fonts)

clock = pygame.time.Clock()

tick_count = 0


while True:
    events = pygame.event.get()

    controller.tick(events)

    pygame.display.flip()
    clock.tick(60)

    #print(tracemalloc.get_traced_memory())
    #tracemalloc.stop()


