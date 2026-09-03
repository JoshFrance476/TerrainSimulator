from models import StorySetup, Location
from story_generation.scene import Scene

class StoryState:
    """Maintains the current state of the story"""
    def __init__(self):
        self.setup = StorySetup()

        self.character_notebook = []  
        self.character_history: list[str] = [] #llm generated scene summaries
        self.stats: dict[str, int] = {} # stat name, value
        self.inventory: list[str] = []

        self.player_location = Location(0, 0)

        self.movement_history = [] # Dicts containing "direction" and "biome" 

        self.quest_list = []

        self.current_scene = None

        self.scene_history: list[Scene] = []

    def get_or_create_scene(self) -> Scene:
        if self.current_scene is None or self.current_scene.ended:
            self.current_scene = Scene()
        return self.current_scene

    def get_scene(self) -> Scene:
        return self.current_scene

    def clear_scene(self):
        self.current_scene = None
    