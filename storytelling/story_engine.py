from storytelling.llm_client import LLMClient
from storytelling.story_state import StoryState
from storytelling.context_builder import ContextBuilder
from storytelling.character_manager import CharacterManager
from storytelling.scene_manager import SceneManager
from storytelling.stream_handler import StreamHandler
 
 
class StoryEngine:
    def __init__(self, world):
        self.world = world
        self.state = StoryState()
        self.llm = LLMClient(self.state)
 
        self.context_builder = ContextBuilder(self.state, self.world)
        self.character_manager = CharacterManager(self.state, self.llm)
        self.scene_manager = SceneManager(self.state, self.llm, self.context_builder)
        self.stream_handler = StreamHandler(self.state, self.scene_manager)
 
    # ------------------------------------------------------------------
    # Public interface (called by InteractionSystem)
    # ------------------------------------------------------------------
 
    def poll(self):
        """Called every frame by the main loop. Returns True if UI needs a refresh."""
        return self.stream_handler.poll()
 
    def generate_scene_interaction(self, selected_cell):
        self.scene_manager.generate_scene_interaction(selected_cell)
 
    def choose_action(self, action, selected_cell):
        scene = self.state.current_scene
        scene.submit_action(action)
        if scene.ended:
            new_quest_list, prompt_tokens, completion_tokens = self.scene_manager.end_scene(scene, selected_cell)
            for quest in new_quest_list:
                self.world.add_new_region_to_chunk(quest["chunk_id"], quest["title"], quest["visible_context"], quest["hidden_context"])
            self.update_tokens(prompt_tokens, completion_tokens)
        else:
            self.scene_manager.generate_scene_interaction(selected_cell)
 
    def clear_scene(self):
        self.scene_manager.clear_scene()
 
    def add_to_movement_history(self, movement):
        self.state.movement_history.append(movement)
 
    def get_token_usage(self):
        return (
            f"Prompt tokens: {self.state.prompt_tokens}. "
            f"Completion tokens: {self.state.completion_tokens}. "
            f"Total cost (gpt-oss-120b): "
            f"{round(self.state.prompt_tokens * 0.000015 + self.state.completion_tokens * 0.00006, 5)} cents"
        )
 
    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
 
    def setup(self, story_setup):
        self.state.world_description = story_setup["world_description"]
        self.state.character_description = story_setup["character_description"]
        self.state.story_focus_description = story_setup["story_focus_description"]
 
    def get_setup(self):
        return {
            "world_description": self.state.world_description,
            "character_description": self.state.character_description,
            "story_focus_description": self.state.story_focus_description
        }
 
    def clear_setup(self):
        self.state.world_description = ""
        self.state.character_description = ""
        self.state.story_focus_description = ""
 
    def setup_character(self, character_desc, world_desc, story_desc):
        prompt_tokens, completion_tokens = self.character_manager.setup_character(
            character_desc, world_desc, story_desc
        )
        self.update_tokens(prompt_tokens, completion_tokens)
 
    def setup_story(self, character_desc, world_desc, story_desc):
        prompt_tokens, completion_tokens, story_list = self.character_manager.setup_story(
            character_desc, world_desc, story_desc
        )
        self.update_tokens(prompt_tokens, completion_tokens)
        return story_list
 
    # ------------------------------------------------------------------
    # Accessors delegated to managers
    # ------------------------------------------------------------------
 
    def get_notebook(self):
        return self.character_manager.get_notebook()
 
    def get_character_history(self):
        return self.character_manager.get_character_history()
 
    def get_current_scene(self):
        return self.scene_manager.get_current_scene()
 
    def get_current_scenario_debug_info(self):
        return self.scene_manager.get_current_scene_debug_info()
 
    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
 
    def update_tokens(self, prompt_tokens, completion_tokens):
        self.state.prompt_tokens += prompt_tokens
        self.state.completion_tokens += completion_tokens