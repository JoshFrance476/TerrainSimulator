from storytelling.scenario import Scenario
from storytelling.story_llm import StoryLLM
import json

class StoryEngine:
    def __init__(self, world, state):
        self.world = world
        self.state = state
        self.llm = StoryLLM()

        #self.story_inspo = self.setup_story(self.state.character_description, self.state.world_description, self.state.story_focus_description)
        self.story_inspo = None
    
    def setup_character(self, character_desc, world_desc, story_desc):
        response = self.llm.prompt_character_setup(character_desc, world_desc, story_desc)
        self.state.notebook = response["notebook"]
        self.state.stats = response["attributes"]
        self.update_tokens(response["prompt_tokens"], response["completion_tokens"])
    
    def setup_story(self, character_desc, world_desc, story_desc):
        response = self.llm.prompt_story_setup(character_desc, world_desc, story_desc)
        self.update_tokens(response["prompt_tokens"], response["completion_tokens"])
        return response["story_list"]

    def setup_scene(self, context):
        response = self.llm.prompt_scene_setup(context, self.state.world_description, self.state.story_focus_description)

        self.state.current_scene = Scenario(focus=response["focus"])


    
    def generate_scene_interaction(self, selected_cell):
        if self.state.current_scene is None:
            context = self._build_context(selected_cell, full_context=True)
            self.setup_scene(context)
        
        context = self._build_context(selected_cell, full_context=False)
        
        if self.state.current_scene.interaction_count == 0:
            response = self.llm.prompt_scene(context, self.state.world_description, self.state.story_focus_description, self.state.current_scene.focus)
        else:
            response = self.llm.prompt_scene(context, self.state.world_description, self.state.story_focus_description)
        self.state.current_scene.set_pending_interaction(response["description"], response["actions"])
        self.update_tokens(response["prompt_tokens"], response["completion_tokens"])
    
    def choose_action(self, action_index, selected_cell):
        scene = self.state.current_scene
        scene.submit_action(action_index)

        if scene.ended:
            response = self.llm.prompt_scene_summary(scene.get_interactions_string(), self.world.get_semantic_chunk_context(selected_cell))
            self.update_tokens(response["prompt_tokens"], response["completion_tokens"])
            self.state.character_history.append(response["summary"])
            new_region = response["new_region"]
            if new_region:
                self.world.add_new_region_to_chunk(new_region["feature_id"], new_region["title"], new_region["visible_description"], new_region["hidden_description"])
            self.state.current_scene = None
        else:
            self.generate_scene_interaction(selected_cell)

    def get_notebook(self):
        return self.state.notebook

    def get_character_history(self):
        return self.state.character_history
    
    def get_current_scenario(self):
        return self.state.current_scene

    def clear_scenario(self):
        self.state.current_scene = None
    
    def add_to_movement_history(self, movement):
        self.state.movement_history.append(movement)

    
    def get_most_recent_movement_json(self):
        if len(self.state.movement_history) > 1:
            current_movement_entry = self.state.movement_history[-1]
            past_movement_entry = self.state.movement_history[-2]
            return {
                "direction": current_movement_entry['direction'],
                "from_biome": past_movement_entry['biome'],
                "to_biome": current_movement_entry['biome']
            }
        else:
            return {}
    
    def _build_scene_setup_context(self, selected_cell):
        tile = self.world.get_tile_data_json(selected_cell)
        current_scenario = self.state.current_scene

        context = {
            ""
            "character_notebook": list(self.state.notebook),
            "previous_scenes_on_other_tiles": list(self.state.character_history),
            "nearby_features": self.world.get_chunk_context_json(selected_cell),
            "current_tile": tile,
            "recent_movement": self.get_most_recent_movement_json()
            
        }
        return json.dumps(context, ensure_ascii=False)
    
    def _build_scene_context(self):
        current_scenario = self.state.current_scene

        context = {
            "tile_interaction_history": current_scenario.get_interactions_json() if current_scenario else None,
            "latest_tile_action": current_scenario.get_most_recent_action() if current_scenario else None,
            "character_notebook": list(self.state.notebook),
            "scene_prompt": self.state.current_scene.focus,
            "scene_environment": self.state.current_scene.environment
        }

        return json.dumps(context, ensure_ascii=False)
    
    def update_tokens(self, prompt_tokens, completion_tokens):
        self.state.prompt_tokens += prompt_tokens
        self.state.completion_tokens += completion_tokens
    
    def get_token_usage(self):
        return f"Prompt tokens: {self.state.prompt_tokens}. Completion tokens: {self.state.completion_tokens}. Total cost (gpt-oss-120b): {round(self.state.prompt_tokens*0.000015+self.state.completion_tokens*0.00006, 5)} cents"

    def get_current_scenario_debug_info(self):
        if self.state.current_scene:
            return {
                "focus": self.state.current_scene.focus, 
                "environment": self.state.current_scene.environment,
                "significance": self.state.current_scene.significance
            }
        else:
            return None