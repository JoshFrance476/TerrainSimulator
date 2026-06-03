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
from pathlib import Path
import numpy as np
import yaml

class AppController:
    def __init__(self, screen, fonts):
        self.world = World(config.WORLD_ROWS, config.WORLD_COLS)
        self.storyteller = StoryEngine(self.world)

        if config.MAP_NAME:
            try:
                self.load_file(config.MAP_NAME, update_interaction_system=False)
            except Exception as e:
                print("invalid map file name - generating procedural map")
                self.generate_map()
        else:
            self.generate_map()

        self.camera = Camera()
        
        self.player = MapEntity(location = (self.world.get_starting_location()), 
                                boundary = (config.WORLD_ROWS, config.WORLD_COLS))
        
        self.camera.set_location(self.player.get_location())

        self.fonts = fonts
        
        self.brush = BrushManager()
        self.app_state = AppState()
        self.world_editor = WorldEditor(self.world, self.brush, self.app_state)

        self.map_renderer = MapRenderer(self.world, self.camera, self.app_state)
        

        self.ui_manager = UIManager(self.app_state, self.camera, self.storyteller, fonts, self.world, self.brush, self.generate_map, self.load_file, self.save_file)
        self.input_system = InputSystem(self.ui_manager)

        self.interaction_system = InteractionSystem(self.app_state, self.camera, self.player, self.world_editor, self.storyteller, self.world, self.brush, self.refresh_map_render, self.ui_manager.mouse_on_map)

        self.interaction_system.init_start()

        self.ui_manager.set_interaction_system(self.interaction_system)
        
        
        self.fps_monitor = FPSMonitor()
        self.render_system = RenderSystem(self.ui_manager, self.map_renderer, self.fps_monitor)

        self.screen = screen
    
    def tick(self, events):
        keys, mouse_pos = self.input_system.continuous()
        self.interaction_system.handle_continuous(keys, mouse_pos)

        commands = self.input_system.build_commands(events)

        for command in commands:
            self.interaction_system.handle(command)

        self.render_system.render(self.screen)
    
    def generate_map(self):
        config_path = Path("data/saved_maps/DefaultConfig.yaml")

        with open(config_path, "r") as f:
            biome_config = yaml.safe_load(f)
        
        self.world.load_data(biome_config)

        self.storyteller.clear_setup()

        self.interaction_system.refresh_render()
    
    def load_file(self, file_name, update_interaction_system = True):
        path = Path("data/saved_maps") / file_name
        map_data_path = path / "map_data.npz"
        biome_config_path = path / "biome_config.yaml"
        story_setup_path = path / "story_setup.yaml"
        
        with open(story_setup_path, "r") as f:
            story_setup = yaml.safe_load(f)

        self.storyteller.setup(story_setup)

        with open(biome_config_path, "r") as f:
            biome_config = yaml.safe_load(f)
        
        world_data = np.load(map_data_path, allow_pickle=True)

        rows, cols = world_data["biome"].shape
        config.WORLD_ROWS = rows
        config.WORLD_COLS = cols
        self.world.rows = rows
        self.world.cols = cols

        self.world.load_data(biome_config, world_data)

        if update_interaction_system:
            self.interaction_system.init_start()
    
    def save_file(self, file_name):
        path = Path("data/saved_maps") / file_name
        path.mkdir(parents=True, exist_ok=True)

        map_data, region_data, biome_config = self.world.get_data()

        story_setup = self.storyteller.get_setup()

        np.savez(
            path / "map_data",
            **map_data,

            region_map=np.array(region_data["map"], dtype=object),
            region_list=np.array(region_data["list"], dtype=object),
        )

        with open(f'{path}/biome_config.yaml', 'w') as f:
            yaml.dump(biome_config, f, sort_keys=False)

        with open(f'{path}/story_setup.yaml', 'w') as f:
            yaml.dump(story_setup, f, sort_keys=False)

    def refresh_map_render(self):
        self.map_renderer.refresh_view()