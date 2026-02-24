from storyteller.scenario import Scenario
from utils.llm_utils import prompt_scenario, prompt_character_setup, prompt_scenario_summary, prompt_story_setup

class StorytellerManager:
    def __init__(self, controller):
        self.controller = controller

        self.world_description = "An alient planet with strange, often dangerous flora and fauna."
        self.character_description = "A space freighter crewmember who has crashlanded on an alien planet. Has no gear, and must fight for survival in an unfamiliar world"  #will just be used to generate an inital character notebook (and maybe history?)
        self.story_focus_description = "The player has crashed landed on this alient planet. In their fight for survival they uncover the beautiful, intricate ecosystem that thrives on this planet."

        self.character_notebook = []
        self.character_history  = []
        self.character_stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

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
    
    def build_prompt(self, scenario = None):
        prompt = ""
        prompt += "World description: "+self.world_description
        prompt += ". Character notebook: "+", ".join(self.character_notebook)
        prompt += ". Character history: "+", ".join(self.character_history)
        prompt += ". Story focus description: "+self.story_focus_description
        prompt += ". Location: "+ str(self.controller.get_semantic_tile_data(self.controller.selected_cell))
        if scenario:
            prompt += ". What has happened in this scenario: "+scenario.get_interactions_string()
        return prompt

    def prompt_new_interaction(self):
        prompt = self.build_prompt(self.current_scenario)
        output_tokens, input_tokens, description, actions = prompt_scenario(prompt)
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
        
    
    def get_notebook(self):
        return self.character_notebook

    def get_character_history(self):
        return self.character_history
        
