from story_generation.llm_client import LLMClient
from story_generation.story_state import StoryState
from story_generation.utils.context_builder import ContextBuilder
from grid_utils import get_cell_radius_indexes

from world import World

from models import Location, SetupDescriptionsBody, StorySetup, StorylinePromptData, MoveDeltaBody

import json
 

class StoryEngine:
    def __init__(self, world: World):
        """Orchestrates story generation by collecting context, calling LLM prompts and updating state and world with responses"""
        self.world = world
        self.state = StoryState()
        self.llm = LLMClient() 
        self.context_builder = ContextBuilder(self.state, self.world)

        self.set_player_location(self.world.starting_location)
 
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
        async for event in self.llm.prompt_interaction(guide, previous_interactions, self.state.setup):
            if event["event"] == "done":
                payload = json.loads(event["payload"])
                scene.add_interaction(
                    description=payload["interaction_description"],
                    actions=payload["player_actions"]
                    )
            yield event

    async def generate_storylines(self, setup: StorylinePromptData):
        async for event in self.llm.prompt_storylines(setup, self.world.component_lookup, self.world.region_lookup):
            yield event

    async def generate_hidden_context(self, storylines):
        response = await self.llm.prompt_hidden_context(storylines, self.world.component_lookup, self.world.region_lookup)
        print(response)
        temp_components = self.world.component_lookup.copy()
        temp_regions = self.world.region_lookup.copy()
        for component in response["components"]:
            temp_components[str(component["component_id"])]["context"] = component["context"]
        for region in response["regions"]:
            temp_regions[str(region["region_id"])]["context"] = region["context"]
        return {
            "components": temp_components,
            "regions": temp_regions
        }

    async def generate_character_setup(self, setup: SetupDescriptionsBody):
        response = await self.llm.prompt_character_setup(setup.character_description, setup.world_description, setup.story_description)
        return response

    async def generate_scene_summary(self):
        response = await self.llm.prompt_scene_summary(self.state.get_scene())
        self.state.character_history.append(response["summary"])
        self.state.scene_history.append(self.state.get_scene())
        self.state.clear_scene()

 
    def clear_scene(self):
        self.state.clear_scene()
 
    def add_to_movement_history(self, movement):
        self.state.movement_history.append(movement)
 
    def get_player_location(self) -> Location:
        return self.state.player_location

    def move_player(self, delta: MoveDeltaBody) -> Location:
        self.state.player_location.x += delta.x
        self.state.player_location.y += delta.y
        self.update_revealed_tiles()
        return self.state.player_location

    def set_player_location(self, location: Location):
        self.state.player_location = location
        self.update_revealed_tiles()

    def update_revealed_tiles(self):
        location = self.state.player_location
        for dx, dy in get_cell_radius_indexes(self.state.player_view_radius):
            x, y = location.x + dx, location.y + dy
            if 0 <= x < self.world.width and 0 <= y < self.world.height:
                self.state.revealed_tiles.add((x, y))

 
    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
 
    def setup(self, story_setup: StorySetup):
        self.state.setup = story_setup
 
    def get_setup(self) -> StorySetup:
        return self.state.setup
 
    def clear_setup(self):
        self.state.setup = StorySetup()
 
    # ------------------------------------------------------------------
    # Accessors delegated to managers
    # ------------------------------------------------------------------
 
    def get_notebook(self):
        return self.state.character_notebook
 
    def get_character_history(self):
        return self.state.character_history
 
    def get_current_scene(self):
        return self.state.get_scene()

    def get_token_usage(self):
        return {
            "input_tokens": self.llm.prompt_tokens,
            "output_tokens": self.llm.completion_tokens
        }