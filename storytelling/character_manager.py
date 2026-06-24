class CharacterManager:
    def __init__(self, state, llm):
        self.state = state
        self.llm = llm
 
    def setup_character(self, character_desc, world_desc, story_desc):
        response = self.llm.prompt_character_setup(character_desc, world_desc, story_desc)
        self.state.notebook = response["notebook"]
        self.state.stats = response["attributes"]
        return response["prompt_tokens"], response["completion_tokens"]
 
    def setup_story(self, character_desc, world_desc, story_desc):
        response = self.llm.prompt_story_setup(character_desc, world_desc, story_desc)
        return response["prompt_tokens"], response["completion_tokens"], response["story_list"]
 
    def get_notebook(self):
        return self.state.notebook
 
    def get_character_history(self):
        return self.state.character_history
 