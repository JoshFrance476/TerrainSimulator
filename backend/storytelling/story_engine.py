from storytelling.llm_client import LLMClient
from storytelling.story_state import StoryState
from storytelling.context_builder import ContextBuilder
from storytelling.scene_manager import SceneManager

from world.world import World

from models import Location, StorySetup

import json
 
 
class StoryEngine:
    def __init__(self, world: World):
        self.world = world
        self.state = StoryState()
        self.llm = LLMClient(self.state) 
        self.player_location = Location(0, 0)
 
        self.context_builder = ContextBuilder(self.state, self.world)
        self.scene_manager = SceneManager(self.state, self.llm, self.context_builder)
 
    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
 
    async def generate_scene_interaction(self, selected_cell: Location):
        async for event in self.scene_manager.generate_scene_interaction(selected_cell):
            yield event
            if event["event"] == "done":
                data = json.loads(event["data"])
                description = data["description"]
                actions = data["actions"]
            if event["event"] == "guide":
                self.state.current_scene.add_interaction(description,
                                                         actions, 
                                                         event["data"]["suggested_outcomes"], 
                                                         event["data"])
                

 
    async def choose_action(self, action: str, selected_cell: Location):
        scene = self.state.current_scene
        scene.submit_action(action)
        if scene.ended:
            new_quest_list = await self.scene_manager.end_scene(scene, selected_cell)
            for quest in new_quest_list:
                self.state.quest_list.append({
                    "title": quest["title"],
                    "visible_context": quest["visible_context"],
                    "hidden_context": quest["hidden_context"]
                })
                self.world.add_new_region_to_chunk(quest["chunk_id"], quest["title"], quest["visible_context"], quest["hidden_context"])
            self.state.quest_list = self.state.quest_list

    async def generate_storylines(self, setup: StorySetup):
        return await self.llm.prompt_storylines(setup)
 
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

    def get_player_location(self) -> Location:
        return self.player_location

    def set_player_location(self, location: Location):
        self.player_location = location
 
    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
 
    def setup(self, story_setup: StorySetup):
        self.state.story_setup = story_setup
 
    def get_setup(self) -> StorySetup:
        return self.state.story_setup
 
    def clear_setup(self):
        self.state.story_setup = StorySetup(
            world_description="",
            character_description="",
            story_focus_description=""
        )
 
    # ------------------------------------------------------------------
    # Accessors delegated to managers
    # ------------------------------------------------------------------
 
    def get_notebook(self):
        return self.state.character_notebook
 
    def get_character_history(self):
        return self.state.character_history
 
    def get_current_scene(self):
        return self.scene_manager.get_current_scene()
    
    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
 
    def update_tokens(self, prompt_tokens: int, completion_tokens: int):
        self.state.prompt_tokens += prompt_tokens
        self.state.completion_tokens += completion_tokens