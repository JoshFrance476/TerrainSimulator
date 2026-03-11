from storytelling.scenario import Scenario
from storytelling.story_llm import StoryLLM
import json

class StoryEngine:
    def __init__(self, world, state):
        self.world = world
        self.state = state
        self.llm = StoryLLM()
    
    def setup_character(self, character_desc, world_desc, story_desc):
        notebook, stats, usage = self.llm.prompt_character_setup(character_desc, world_desc, story_desc)
        self.state.notebook = notebook
        self.state.stats = stats
    
    def begin_or_continue_scene(self, selected_cell):
        context = self._build_context(selected_cell)
        response = self.llm.prompt_scene(context, self.state.world_description, self.state.story_focus_description)

        if self.state.current_scene is None:
            self.state.current_scene = Scenario()
        
        self.state.current_scene.set_pending_interaction(response["description"], response["actions"])
    
    def choose_action(self, action_index, selected_cell):
        scene = self.state.current_scene
        scene.submit_action(action_index)

        if scene.ended:
            response = self.llm.prompt_scene_summary(scene.get_interactions_string(), self.world.get_semantic_chunk_context(selected_cell))
            self.state.character_history.append(response["summary"])
            new_region = response["new_region"]
            if new_region:
                self.world.add_new_region_to_chunk(new_region["feature_id"], new_region["title"], new_region["visible_description"], new_region["hidden_description"])
            self.state.current_scene = None
        else:
            self.begin_or_continue_scene(selected_cell)

    def get_notebook(self):
        return self.state.notebook

    def get_character_history(self):
        return self.state.character_history
    
    def get_current_scenario(self):
        return self.state.current_scene

    def clear_scenario(self):
        self.state.current_scene = None

    
    def get_most_recent_movement_string(self):
        if len(self.state.movement_history) > 1:
            current_movement_entry = self.state.movement_history[-1]
            past_movement_entry = self.state.movement_history[-2]
            return f"Moved {current_movement_entry['direction']} from {past_movement_entry['biome']} to {current_movement_entry['biome']}"
        else:
            return None
    
    def _build_context(self, selected_cell):
        tile = self.world.get_semantic_tile_data(selected_cell)
        current_scenario = self.state.current_scene

        context = {
            "character": {
                "notebook": list(self.state.notebook),
                "previous_actions_on_other_tiles": list(self.state.character_history),
            },
            "movement": self.get_most_recent_movement_string(),
            "tile": tile,
            "previous_events_on_this_tile": current_scenario.get_interactions_string() if current_scenario else None,
            "most_recent_action_on_this_tile": current_scenario.get_most_recent_action() if current_scenario else None,
            "location_context": self.world.get_semantic_chunk_context(selected_cell)
        }
        return json.dumps(context, ensure_ascii=False)