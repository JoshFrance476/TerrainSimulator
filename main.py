import pygame
import utils.config as config
from camera import Camera
from event_handler import EventHandler
from simulation.simulator import Simulator
from rendering.map_renderer import MapRenderer
from rendering.ui_manager import UIManager

pygame.init()

# Initialize screen
screen = pygame.display.set_mode((config.WIDTH + config.SIDEBAR_WIDTH, config.HEIGHT), pygame.RESIZABLE)
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
        simulator.update()


    
    # Render everything
    screen.fill((0, 0, 0))
    map_renderer.draw_map(screen, simulator.get_display_map(), simulator.get_step_counter(), camera)
    ui_manager.draw_sidebar(screen, simulator.selected_cell, simulator.get_static_maps())


    pygame.display.flip()
    clock.tick(20)
