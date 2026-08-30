from storytelling.llm_client import LLMClient
from storytelling.story_state import StoryState
from storytelling.context_builder import ContextBuilder

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
 
    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
 
    async def choose_action(self, action: str):
        self.state.current_scene.submit_action(action)

    async def generate_scene_guide(self, selected_cell: Location):
        context = self.context_builder.build_scene_guide_context(selected_cell)

        scene = self.state.get_or_create_scene()
        scene_history = scene.get_history()
        
        async for event in self.llm.prompt_scene_guide(context, scene_history, "medium"):
            if event["event"] == "done":
                scene.set_guide(json.loads(event["payload"]))
            yield event

    async def generate_interaction(self):
        scene = self.state.get_scene()
        guide = scene.guide
        previous_interactions = scene.get_history()
        async for event in self.llm.prompt_interaction(guide, previous_interactions):
            if event["event"] == "done":
                payload = json.loads(event["payload"])
                scene.add_interaction(
                    description=payload["interaction_description"],
                    actions=payload["player_actions"]
                    )
            yield event

    async def generate_storylines(self, setup: StorySetup):
        async for event in self.llm.prompt_storylines(setup, self.world.component_lookup, self.world.region_lookup):
            yield event

    async def generate_hidden_context(self, storylines):
        response = await self.llm.prompt_hidden_context(storylines, self.world.component_lookup, self.world.region_lookup)
        print(response)
        for component in response["components"]:
            self.world.component_lookup[str(component["component_id"])]["context"] = component["context"]
        return self.world.component_lookup

    async def generate_scene_summary(self):
        response = await self.llm.prompt_scene_summary(self.state.get_scene())
        self.state.character_history.append(response["summary"])
        self.state.scene_history.append(self.state.get_scene())
        self.state.clear_scene()

 
    def clear_scene(self):
        self.state.clear_scene()
 
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
        return self.state.get_scene()
    
    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
 
    def update_tokens(self, prompt_tokens: int, completion_tokens: int):
        self.state.prompt_tokens += prompt_tokens
        self.state.completion_tokens += completion_tokens