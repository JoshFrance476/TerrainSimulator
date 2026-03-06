import pygame
import config as config
from app.app_controller import AppController
from generation.biome_config_manager import BiomeConfigManager
import json

#import tracemalloc
#tracemalloc.start()

pygame.init()

class FontManager:
    def __init__(self):
        self.header = pygame.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE+3)
        self.large_font = pygame.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)
        self.small_font = pygame.font.Font("assets/fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE-3)



# Initialize screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH + config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Terrain Generation")

fonts = FontManager()

biome_config_manager = BiomeConfigManager()

with open("biome_config.json", "r", encoding="utf-8") as f:
    biome_config = json.load(f)

biome_config_manager.load_biome_config_file(biome_config)

controller = AppController(screen, fonts, biome_config_manager)

clock = pygame.time.Clock()

tick_count = 0




while True:
    events = pygame.event.get()

    controller.tick(events)

    pygame.display.flip()
    clock.tick(config.TARGET_FPS)

    #print(tracemalloc.get_traced_memory())
    #tracemalloc.stop()


