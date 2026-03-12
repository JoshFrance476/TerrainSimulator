class StoryState:
    def __init__(self):
        self.world_description = """The world is abandoned and desolate. The remaining structures are in ruins. There are no signs remaining humans or animals.
        There is a constant sense of danger and tension even though no life forms are encountered. 20th Soviet-style architecture.
        """
        self.character_description = """A lone wanderer, not sure what to make of the world around him. The character is paranoid and has a sense that there is someone or something lurking nearby, influencing the world but just out of sight"""  
        self.story_focus_description = """The environment is vast and empty. There is a constant sense of tension as the player travels across the land."""

        self.notebook = []
        self.character_history = []
        self.stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

        self.movement_history = [] # Dicts containing "direction" and "biome"

        self.current_scene = None

        self.completion_tokens = 0
        self.prompt_tokens = 0