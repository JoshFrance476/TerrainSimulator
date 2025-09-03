import pygame
import utils.config as config
from camera import Camera
from input_handler import EventHandler
from simulation.world_data import WorldData
from simulation.world import World
from rendering.map_renderer import MapRenderer
from rendering.ui_manager import UIManager



#import tracemalloc
#tracemalloc.start()

pygame.init()

# Initialize screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH + config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Terrain Generation")

# Initialize core objects
camera = Camera()
event_handler = EventHandler()
world = World(config.WORLD_ROWS, config.WORLD_COLS)
map_renderer = MapRenderer()
ui_manager = UIManager()

clock = pygame.time.Clock()


while True:
    event_handler.handle_events(camera)

    camera.clamp_pan()
    
    if not event_handler.paused:
        world.step()

    
    map_renderer.render_view(screen, 
                             world.get_region_data(camera.x_pos, 
                                                        camera.y_pos, 
                                                        config.CAMERA_COLS+camera.x_pos, 
                                                        config.CAMERA_ROWS+camera.y_pos), 
                            event_handler.get_selected_filter())
    
    ui_manager.render_ui(screen, 
                         world.get_cell_data(event_handler.selected_cell), 
                         world.get_all_settlements(),
                         camera.x_pos, 
                         camera.y_pos, 
                         map_renderer.get_selected_filter_name(), 
                         event_handler.get_relevant_cells())
    

    pygame.display.flip()
    clock.tick(60)

    #print(tracemalloc.get_traced_memory())
    #tracemalloc.stop()


