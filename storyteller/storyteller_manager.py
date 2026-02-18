from storyteller.scenario import Scenario
from utils.llm_utils import prompt_scenario

class StorytellerManager:
    def __init__(self, controller):
        self.controller = controller

        self.world_description = "A game of thrones inspired world"
        self.character_description = "A young man yet to make a name for himself"  #will just be used to generate an inital character notebook (and maybe history?)
        self.story_focus_description = "The player will embark on an adventure across the realm, meeting interesting characters as they go. The player should not be given options to 'go along' with NPCs or work for them."

        self.character_notebook = []
        self.character_history  = []
        self.character_stats = {}
        self.tile_history = {}  #key is location tuple, value is list of 'history' strings

        self.current_scenario = None

    def create_scenario(self):
        new_scenario = Scenario()
        return new_scenario
    
    def build_prompt(self, scenario = None):
        prompt = ""
        prompt += "World description: "+self.world_description
        prompt += "\nCharacter description: "+self.character_description
        prompt += "\nStory focus description: "+self.story_focus_description
        prompt += "\n Location: "+ str(self.controller.get_semantic_tile_data(self.controller.selected_cell))
        if scenario:
            prompt += "\nWhat has happened in this scenario: "+scenario.get_interactions_string()
        return prompt

    def prompt_new_interaction(self):
        prompt = self.build_prompt(self.current_scenario)
        description, exit_flag, actions = prompt_scenario(prompt)
        if self.current_scenario:
            self.current_scenario.set_pending_interaction(description, actions)
        else:
            new_scenario = self.create_scenario()
            new_scenario.set_pending_interaction(description, actions)
            self.current_scenario = new_scenario
    
    def submit_action(self, action_index):
        self.current_scenario.sumbit_action(action_index)
        self.prompt_new_interaction()
        
