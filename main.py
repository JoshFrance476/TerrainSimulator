import pygame
import config as config
from app_controller import AppController
from utils.biome_config_manager import BiomeConfigManager

#import tracemalloc
#tracemalloc.start()

pygame.init()

class FontManager:
    def __init__(self):
        self.header = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE+3)
        self.large_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)
        self.small_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE-3)



# Initialize screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH + config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Terrain Generation")

fonts = FontManager()

biome_config = BiomeConfigManager()

biome_config.load_biome_config_file("biome_config.json")

controller = AppController(screen, fonts, biome_config)

clock = pygame.time.Clock()

tick_count = 0




while True:
    events = pygame.event.get()

    controller.tick(events)

    pygame.display.flip()
    clock.tick(config.TARGET_FPS)

    #print(tracemalloc.get_traced_memory())
    #tracemalloc.stop()


