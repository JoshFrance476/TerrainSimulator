class StoryState:
    def __init__(self):
        self.world_description = ""
        self.character_description = ""  
        self.story_focus_description = ""

        self.notebook = []
        self.character_history = []
        self.stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

        self.movement_history = [] # Dicts containing "direction" and "biome"

        self.current_scene = None

        self.completion_tokens = 0
        self.prompt_tokens = 0
    