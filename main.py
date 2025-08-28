import pygame
import utils.config as config
from camera import Camera
from event_handler import EventHandler
from simulation.simulator import Simulator
from rendering.map_renderer import MapRenderer
from rendering.ui_manager import UIManager

pygame.init()

# Initialize screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH + config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Terrain Generation")

# Initialize core objects
camera = Camera()
event_handler = EventHandler()
simulator = Simulator()
map_renderer = MapRenderer()
ui_manager = UIManager()

clock = pygame.time.Clock()

while True:
    event_handler.handle_events(camera)

    
    if not event_handler.paused:
        simulator.update(event_handler.selected_filter)
    
    # Render everything
    screen.fill((0, 0, 0))
    map_renderer.draw_map(screen, simulator.get_display_map(), camera)
    ui_manager.draw_sidebar(event_handler.selected_cell, screen, simulator.get_static_maps(), simulator.get_dynamic_maps())
    ui_manager.draw_hover_highlight(event_handler.hovered_cell, screen, camera.x_pos, camera.y_pos)

    if event_handler.selected_cell:
        ui_manager.draw_selected_cell_border(event_handler.selected_cell, screen, camera.x_pos, camera.y_pos, config.CELL_SIZE)
    



    pygame.display.flip()
    clock.tick(20)
