import queue

class StoryState:
    def __init__(self):
        self.world_desc = ""
        self.character_desc = ""  
        self.story_focus_desc = ""

        self.notebook = []
        self.character_history = []
        self.stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

        self.movement_history = [] # Dicts containing "direction" and "biome"

        self.current_scene = None

        self.chunk_queue = queue.Queue()
        self.is_streaming = False
        self.stream_response = ""

        self.completion_tokens = 0
        self.prompt_tokens = 0
    