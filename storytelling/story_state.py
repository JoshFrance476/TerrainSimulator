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
    
    def get_setup(self):
        return {
            "world_description": self.world_description, 
            "character_description": self.character_description, 
            "story_focus_description": self.story_focus_description
        }
    
    def setup(self, story_setup):
        self.world_description = story_setup['world_description']
        self.character_description = story_setup['character_description']
        self.story_focus_description = story_setup['story_focus_description']