import pygame
import config
from app.app_state import AppState
from editor.world_editor import WorldEditor
from rendering.map_renderer import MapRenderer
from rendering.ui.ui_manager import UIManager
from rendering.camera import Camera
from world.world import World
from world.map_entity import MapEntity
from utils.fps_monitor import FPSMonitor
from storytelling.story_engine import StoryEngine
from editor.brush_manager import BrushManager
from app.input_system import InputSystem
from app.interaction_system import InteractionSystem
from app.render_system import RenderSystem
from storytelling.story_state import StoryState

class AppController:
    def __init__(self, screen, fonts):
        self.world = World(config.WORLD_ROWS, config.WORLD_COLS)
        #self.world.load_map('ColonialFantasy')
        self.world.generate_map()
        self.camera = Camera()
        
        self.player = MapEntity(location = (self.world.get_starting_location()), 
                                boundary = (config.WORLD_ROWS, config.WORLD_COLS))
        
        self.camera.set_location(self.player.get_location())

        self.fonts = fonts
        
        self.brush = BrushManager()
        self.app_state = AppState()
        self.world_editor = WorldEditor(self.world, self.brush, self.app_state)

        self.map_renderer = MapRenderer(self.world, self.camera, self.app_state)

        self.story_state = StoryState()
        self.storyteller = StoryEngine(self.world, self.story_state)
        

        self.ui_manager = UIManager(self.app_state, self.camera, self.storyteller, fonts, self.world, self.brush.get_attributes)
        self.input_system = InputSystem(self.ui_manager, self.get_cell_at_mouse_position)

        self.interaction_system = InteractionSystem(self.app_state, self.camera, self.player, self.world_editor, self.storyteller, self.world, self.brush, self.refresh_map_render, self.get_cell_at_mouse_position, self.ui_manager.mouse_on_map)

        self.ui_manager.set_interaction_system(self.interaction_system)
        
        
        self.fps_monitor = FPSMonitor()
        self.render_system = RenderSystem(self.ui_manager, self.map_renderer, self.fps_monitor)

        self.screen = screen
    
    def tick(self, events):
        keys = self.input_system.continuous()
        self.interaction_system.handle_continuous(keys)

        commands = self.input_system.build_commands(events)

        for command in commands:
            self.interaction_system.handle(command)

        self.render_system.render(self.screen)


    def get_cell_at_mouse_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
            
        # Convert screen coordinates to world coordinates
        world_x = (mouse_x - config.SIDEBAR_WIDTH) + (self.camera.x_pos * config.CELL_SIZE)
        world_y = mouse_y + (self.camera.y_pos * config.CELL_SIZE)

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        return (cell_y, cell_x)

    def refresh_map_render(self):
        self.map_renderer.refresh_view()
