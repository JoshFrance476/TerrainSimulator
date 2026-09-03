from models import Location, SceneContext
from story_generation.story_state import StoryState
from world import World

class ContextBuilder:
    """Collects data from story state and world to build context for prompts."""
    def __init__(self, state: StoryState, world: World):
        
        self.state = state
        self.world = world
 
    def get_movement_history(self):
        if len(self.state.movement_history) > 1:
            current_movement_entry = self.state.movement_history[-1]
            past_movement_entry = self.state.movement_history[-2]
            return {
                "direction": current_movement_entry["direction"],
                "from_biome": past_movement_entry["biome"],
                "to_biome": current_movement_entry["biome"]
            }
        return {}
 
    def build_scene_guide_context(self, selected_cell: Location) -> SceneContext:
        return SceneContext(
            tile_data=self.world.get_cell_data(selected_cell),
            movement_history=self.get_movement_history(),
            character_notebook=self.state.character_notebook,
            story_setup=self.state.story_setup
        )