from storyteller.scenario import Scenario
from utils.llm_utils import prompt_scenario, prompt_notebook_setup, prompt_scenario_summary

class StorytellerManager:
    def __init__(self, controller):
        self.controller = controller

        self.world_description = "A sparsely populated realm with strange, alien flora and fauna."
        self.character_description = "A wandering traveler with expert knowledge of the alien world they live in"  #will just be used to generate an inital character notebook (and maybe history?)
        self.story_focus_description = "The player will embark on an adventure across the realm, learning the secrets of the world. The player should not be given options to 'go along' with NPCs or work for them."

        self.character_notebook = []
        self.character_history  = []
        self.character_stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

        self.current_scenario = None

        self.input_token_count = 0
        self.output_token_count = 0

        self.setup_notebook()
    
    def update_token_counts(self, output_tokens, input_tokens):
        self.output_token_count += output_tokens
        self.input_token_count += input_tokens

    def setup_notebook(self):
        output_tokens, input_tokens, notebook = prompt_notebook_setup(self.character_description)
        self.update_token_counts(output_tokens, input_tokens)

        self.character_notebook = notebook
        
    def create_scenario(self):
        new_scenario = Scenario()
        return new_scenario
    
    def build_prompt(self, scenario = None):
        prompt = ""
        prompt += "World description: "+self.world_description
        prompt += "\nCharacter notebook: "+", ".join(self.character_notebook)
        prompt += "\nStory focus description: "+self.story_focus_description
        prompt += "\n Location: "+ str(self.controller.get_semantic_tile_data(self.controller.selected_cell))
        if scenario:
            prompt += "\nWhat has happened in this scenario: "+scenario.get_interactions_string()
        return prompt

    def prompt_new_interaction(self):
        prompt = self.build_prompt(self.current_scenario)
        output_tokens, input_tokens, description, exit_flag, actions = prompt_scenario(prompt, self.character_notebook)
        self.update_token_counts(output_tokens, input_tokens)
        if exit_flag:
            self.current_scenario.add_interaction(description, "End scenario")
            output_tokens, input_tokens, self.character_notebook = prompt_scenario_summary(self.current_scenario.get_interactions_string(), self.character_notebook)
            self.update_token_counts(output_tokens, input_tokens)
        else:
            if self.current_scenario:
                self.current_scenario.set_pending_interaction(description, actions)
            else:
                new_scenario = self.create_scenario()
                new_scenario.set_pending_interaction(description, actions)
                self.current_scenario = new_scenario
    
    def submit_action(self, action_index):
        self.current_scenario.sumbit_action(action_index)
        self.prompt_new_interaction()
    
    def get_notebook(self):
        return self.character_notebook
        
