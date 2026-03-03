from storyteller.scenario import Scenario
from utils.llm_utils import prompt_scenario, prompt_character_setup, prompt_scenario_summary, prompt_story_setup
import json

class StorytellerManager:
    def __init__(self, world, state):
        self.world = world
        self.state = state

        self.world_description = """An isolated alien planet with breathable air and unstable weather patterns. The flora and fauna grow to immense scale—tree canopies like continents, migratory beasts the size of buildings, root systems that reshape the terrain.
Scattered across the landscape are enormous landmarks: fossilized titans embedded in cliffs, abandoned orbital elevators fused into mountainsides, and vast metallic rings half-swallowed by forest. Their purpose is unknown. The planet shows signs of a powerful past civilization, but no living architects remain.
The ecosystem is active, reactive, and sometimes hostile. Survival depends on adaptation."""
        self.character_description = """A wandering human traveller with practical survival skills and no permanent home. You move between settlements trading knowledge, scavenged technology, and rare biological samples in exchange for tools, repairs, and information.
You are resourceful rather than powerful—skilled in navigation, field repairs, foraging, and reading environmental signs. You carry modular equipment suited for long-distance travel: weather-resistant clothing, improvised tools, salvaged tech of uncertain origin, and a personal journal documenting routes, ruins, and rumors.
You are cautious but curious. The unknown does not deter you; it compels you. You seek both survival and understanding. Each landmark, creature, and abandoned structure may hold fragments of the planet's history—and possibly clues to why humanity remains stranded here."""  #will just be used to generate an inital character notebook (and maybe history?)
        self.story_focus_description = """A grounded survival narrative centered on exploration and gradual discovery. The tone should emphasize isolation, scale, and the fragility of human life against an overwhelming environment.
Conflicts arise from environmental hazards, resource scarcity and unpredictable megafauna. Solutions rely on adaptation and creative use of limited tools.
The unfolding story reveals the planet's fabled past indirectly—through landmarks, ruins, biological anomalies and environmental clues.
Encounters should feel realistic within the world's internal logic. Progress is earned through careful decision-making, risk management, and learning from prior experiences."""

        self.character_notebook = []
        self.character_history  = []
        self.character_stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

        self.movement_history = [] # Dicts containing "direction" and "biome"

        self.current_scenario = None

        self.input_token_count = 0
        self.output_token_count = 0

        #self.setup_notebook_and_stats()
    
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
            "recent_events_on_this_tile": scenario.get_interactions_string() if scenario else None,
            "most_recent_action_on_this_tile": scenario.get_most_recent_action() if scenario else None
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
        
