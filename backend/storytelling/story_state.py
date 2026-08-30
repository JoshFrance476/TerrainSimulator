from models import StorySetup
from storytelling.scene import Scene

class StoryState:
    def __init__(self):
        self.story_setup = StorySetup(
            world_description="",
            character_description="",
            story_focus_description=""
        )

        self.character_notebook = []
        self.character_history = []
        self.stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

        self.movement_history = [] # Dicts containing "direction" and "biome"

        self.quest_list = []

        self.current_scene = None

        self.scene_history: list[Scene] = []

        self.completion_tokens = 0
        self.prompt_tokens = 0

    def get_or_create_scene(self) -> Scene:
        if self.current_scene is None or self.current_scene.ended:
            self.current_scene = Scene()
        return self.current_scene

    def get_scene(self) -> Scene:
        return self.current_scene
    