from storytelling.scene import Scenario
from storytelling.story_llm import StoryLLM
from storytelling.story_state import StoryState
import json
import random

class StoryEngine:
    def __init__(self, world):
        self.world = world
        self.state = StoryState()
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

    def setup_scene(self, context, prev_scene_outcome):
        signficance_options = ["Very low", "Low", "Medium", "High"]
        scene_significance = signficance_options[random.randint(0, len(signficance_options)-1)]
        if self.state.current_scene:
            response = self.llm.prompt_scene_setup(context, self.state.world_description, self.state.story_focus_description, self.state.character_description, scene_significance, self.state.notebook, prev_scene_outcome, self.state.current_scene.get_outcomes())
        else:
            response = self.llm.prompt_scene_setup(context, self.state.world_description, self.state.story_focus_description, self.state.character_description, scene_significance, self.state.notebook, prev_scene_outcome)
        return response["guide"]


    
    def generate_scene_interaction(self, selected_cell):
        if self.state.current_scene:
            prev_scene_outcome = self.state.current_scene.get_most_recent_outcome()
        else:
            prev_scene_outcome = ""
        scene_guide = self.setup_scene(self._build_scene_setup_context(selected_cell), prev_scene_outcome)

        if self.state.current_scene:
            self.state.current_scene.guide = scene_guide
        else:
            self.state.current_scene = Scenario(scene_guide)
        
        context = self._build_scene_context()
        
        response = self.llm.prompt_scene(context, self.state.world_description, self.state.story_focus_description)
        self.state.current_scene.set_pending_interaction(response["description"], response["actions"], scene_guide["outcome_suggestions"])
        self.update_tokens(response["prompt_tokens"], response["completion_tokens"])
    

    def choose_action(self, action, selected_cell):
        scene = self.state.current_scene
        scene.submit_action(action)

        if scene.ended:
            self.end_scene(scene, selected_cell)
        else:
            self.generate_scene_interaction(selected_cell)
    
    def end_scene(self, scene, selected_cell):
        response = self.llm.prompt_scene_summary(scene.get_interactions_json(), self.world.get_chunk_context_json(selected_cell))
        self.update_tokens(response["prompt_tokens"], response["completion_tokens"])
        self.state.character_history.append(response["summary"])
        new_quests = response["new_quests"]
        for quest in new_quests:
            print(f"Adding quest: {quest['chunk_id']} {quest['title']} {quest['visible_description']} {quest['hidden_description']}")
            self.world.add_new_region_to_chunk(quest["chunk_id"], quest["title"], quest["visible_description"], quest["hidden_description"])
        self.state.current_scene = None

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

        context = {
            "nearby_chunks": self.world.get_chunk_context_json(selected_cell),
            "current_tile": tile,
            "recent_movement": self.get_most_recent_movement_json(),
            
        }
        return json.dumps(context, ensure_ascii=False)
    
    def _build_scene_context(self):
        current_scenario = self.state.current_scene

        context = {
            "tile_interaction_history": current_scenario.get_interactions_json() if current_scenario else None,
            "latest_tile_action": current_scenario.get_most_recent_action() if current_scenario else None,
            "character_notebook": list(self.state.notebook),
            "scene_guide": self.state.current_scene.guide,
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
    
    def setup(self, story_setup):
        self.state.world_description = story_setup['world_description']
        self.state.character_description = story_setup['character_description']
        self.state.story_focus_description = story_setup['story_focus_description']
    
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