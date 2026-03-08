from storytelling.scenario import Scenario
from storytelling.llm_prompting import prompt_scenario, prompt_character_setup, prompt_scenario_summary, prompt_story_setup
import json
from config import INITIALISE_NOTEBOOK_AND_STATS

class StorytellerManager:
    def __init__(self, world, state):
        self.world = world
        self.state = state

        self.world_description = """The map focuses on a a mysterious continent that has begun to be colonised by a british-empire like civilisation. 
        The continent was untouched by humans until it began to be colonised.
        The coast is largely plains, but the interior is covered in dense forests and huge mountain ranges. 
        Only two major towns sit on the coastline, and the interior is unexplored.
        Contact with the empire is rare and the colonists are only just starting to discover the strange and mythical creatures that populate the continent interior.
        The settled coastline is growing quickly with new colonist arriving frequently, but fear and curiosity is spreading about the interior. 
        """
        self.character_description = """An explorer who has just arrived on the continent. They have a backpack with a set of useful exploring tools. They were inspired by
        reports of strange fauna and have come to investigate. They are well-received by locals, who can sense the determination of the character."""  
        self.story_focus_description = """A grounded survival narrative focusing on the player interacting with the locals and exploring the continent interior to discover it's mysteries. 
        The player will spend their time travelling the region, but will face hardships and setbacks, as well as friendly, welcoming locals that want to help the player in the expedition.
        Tone and framing:
        The world should feel like a newly explored frontier.
        The environment is vast, poorly understood, and only partially mapped.
        Occasional references to tracks, survey marks, abandoned camps, or signs of earlier expeditions may appear.
        The tone should feel exploratory rather than adventurous."""

        self.character_notebook = []
        self.character_history  = []
        self.character_stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

        self.movement_history = [] # Dicts containing "direction" and "biome"

        self.current_scenario = None

        self.input_token_count = 0
        self.output_token_count = 0

        if INITIALISE_NOTEBOOK_AND_STATS:
            self.setup_notebook_and_stats()
    
    def update_token_counts(self, output_tokens, input_tokens):
        self.output_token_count += output_tokens
        self.input_token_count += input_tokens

    def setup_notebook_and_stats(self):
        #output_tokens, input_tokens, story_list = prompt_story_setup(self.character_description, self.world_description, self.story_focus_description)
        #self.update_token_counts(output_tokens, input_tokens)
        output_tokens, input_tokens, notebook, stat_list = prompt_character_setup(self.character_description, self.world_description, self.story_focus_description)
        self.update_token_counts(output_tokens, input_tokens)

        self.character_notebook = notebook
        
    def create_scenario(self):
        new_scenario = Scenario()
        return new_scenario

    def get_most_recent_movement_string(self):
        if len(self.movement_history) > 1:
            current_movement_entry = self.movement_history[-1]
            past_movement_entry = self.movement_history[-2]
            return f"Moved {current_movement_entry['direction']} from {past_movement_entry['biome']} to {current_movement_entry['biome']}"
        else:
            return None
    
    def build_prompt(self, scenario = None):
        tile = self.world.get_semantic_tile_data(self.state.selected_cell)

        context = {
            "character": {
                "notebook": list(self.character_notebook),   # durable facts
                "previous_actions_on_other_tiles": list(self.character_history),     # keep SHORT (e.g., last 2–5)
            },
            "movement": self.get_most_recent_movement_string(),
            "tile": tile,
            "previous_events_on_this_tile": scenario.get_interactions_string() if scenario else None,
            "most_recent_action_on_this_tile": scenario.get_most_recent_action() if scenario else None,
            "location_context": self.world.get_semantic_chunk_context(self.state.selected_cell)
        }

        # IMPORTANT: keep this compact; avoid indent in production to save tokens.
        return "CONTEXT_JSON:\n" + json.dumps(context, ensure_ascii=False)

    def prompt_new_interaction(self):
        prompt = self.build_prompt(self.current_scenario)
        output_tokens, input_tokens, description, actions = prompt_scenario(prompt, self.world_description, self.story_focus_description)
        self.update_token_counts(output_tokens, input_tokens)
        if self.current_scenario:
            self.current_scenario.set_pending_interaction(description, actions)
        else:
            new_scenario = self.create_scenario()
            new_scenario.set_pending_interaction(description, actions)
            self.current_scenario = new_scenario
    
    def submit_action(self, action_index):
        self.current_scenario.submit_action(action_index)
        if self.current_scenario.ended:
            output_tokens, input_tokens, self.character_notebook, summary = prompt_scenario_summary(self.current_scenario.get_interactions_string(), self.character_notebook)
            self.character_history.append(summary)
            self.update_token_counts(output_tokens, input_tokens)
        else:
            self.prompt_new_interaction()
        
    def submit_custom_action(self, action_desc):
        self.current_scenario.submit_custom_action(action_desc)
        if self.current_scenario.ended:
            output_tokens, input_tokens, self.character_notebook, summary = prompt_scenario_summary(self.current_scenario.get_interactions_string(), self.character_notebook)
            self.character_history.append(summary)
            self.update_token_counts(output_tokens, input_tokens)
        else:
            self.prompt_new_interaction()

    def get_current_scenario(self):
        return self.current_scenario
    
    def get_notebook(self):
        return self.character_notebook

    def get_character_history(self):
        return self.character_history
        
