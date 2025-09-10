import pygame
import utils.config as config
from camera import Camera
from input_handler import EventHandler
from simulation.world_data import WorldData
from simulation.world import World
from rendering.map_renderer import MapRenderer
from rendering.ui_manager import UIManager
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

# Initialize core objects
world = World(config.WORLD_ROWS, config.WORLD_COLS)

fonts = FontManager()

camera = Camera()

controller = AppController(world, camera)
ui_manager = UIManager(fonts, controller)
map_renderer = MapRenderer(controller)
event_handler = EventHandler(controller)

clock = pygame.time.Clock()

tick_count = 0


while True:
    events = pygame.event.get()

    for event in events:
        event_handler.handle_event(event)
        ui_manager.handle_event(event)
    
    event_handler.handle_continuous_inputs()

    controller.update()

    map_renderer.render_view(screen)
    
    ui_manager.render_ui(screen, world)
    
    if controller.magnified:
        map_renderer.render_magnifier(screen)

    pygame.display.flip()
    clock.tick(60)

    #print(tracemalloc.get_traced_memory())
    #tracemalloc.stop()


