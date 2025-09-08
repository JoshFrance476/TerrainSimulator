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

class FontManager:
    def __init__(self):
        self.large_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)
        self.small_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE-3)



# Initialize screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH + config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Terrain Generation")

# Initialize core objects
camera = Camera()
event_handler = EventHandler()
world = World(config.WORLD_ROWS, config.WORLD_COLS)
map_renderer = MapRenderer()
fonts = FontManager()
ui_manager = UIManager(fonts)



clock = pygame.time.Clock()

tick_count = 0


while True:
    events = pygame.event.get()
    
    event_handler.handle_events(events, camera)

    for event in events:
        ui_manager.handle_event(event)

    camera.clamp_pan()
    
    if not event_handler.paused:
        world.step(tick_count)
        tick_count += 1
    
    screen_data = world.get_region_data(camera.x_pos, 
                                        camera.y_pos, 
                                        config.CAMERA_COLS+camera.x_pos, 
                                        config.CAMERA_ROWS+camera.y_pos)
    
    map_renderer.render_view(screen, 
                             screen_data, 
                            event_handler.get_selected_filter())
    
    
    ui_manager.render_ui(screen, 
                         world.get_cell_data(event_handler.selected_cell),
                         event_handler.get_active_screens(), 
                         world.get_all_settlements(),
                         world.get_all_states(),
                         camera.x_pos, 
                         camera.y_pos, 
                         map_renderer.get_selected_filter_name(), 
                         event_handler.get_relevant_cells(),)
    
    if event_handler.magnified:
        selected_cell, hovered_cell = event_handler.get_relevant_cells()
        map_renderer.render_magnifier(screen, 
                                      world.get_region_data(hovered_cell[1]-config.MAGNIFIER_CELL_AMOUNT, 
                                                            hovered_cell[0]-config.MAGNIFIER_CELL_AMOUNT, 
                                                            hovered_cell[1]+config.MAGNIFIER_CELL_AMOUNT, 
                                                            hovered_cell[0]+config.MAGNIFIER_CELL_AMOUNT),
                                      event_handler.get_selected_filter(),
                                      event_handler.hovered_cell,
                                      camera.x_pos,
                                      camera.y_pos)


    
    

    pygame.display.flip()
    clock.tick(60)

    #print(tracemalloc.get_traced_memory())
    #tracemalloc.stop()


