import pygame
import utils.config as config
from camera import Camera
from event_handler import EventHandler
from worldData import WorldData
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
worldData = WorldData()
world = World()
map_renderer = MapRenderer()
ui_manager = UIManager()

clock = pygame.time.Clock()


while True:
    #Handle keyboard and mouse inputs
    event_handler.handle_events(camera)

    # Ensure camera stays within world bounds
    camera.clamp_pan()
    
    #if not event_handler.paused:
        #world.update()


    # Render everything
    map_renderer.render_view(screen, worldData.get_region_data(camera.x_pos, camera.y_pos, config.CAMERA_COLS+camera.x_pos, config.CAMERA_ROWS+camera.y_pos), event_handler.get_selected_filter())
    ui_manager.draw_sidebar(event_handler.selected_cell, screen, worldData.get_world_data())
    ui_manager.draw_hover_highlight(event_handler.hovered_cell, screen, camera.x_pos, camera.y_pos)

    if event_handler.selected_cell:
        ui_manager.draw_selected_cell_border(event_handler.selected_cell, screen, camera.x_pos, camera.y_pos, config.CELL_SIZE)
    



    pygame.display.flip()
    clock.tick(60)

    #print(tracemalloc.get_traced_memory())
    #tracemalloc.stop()


