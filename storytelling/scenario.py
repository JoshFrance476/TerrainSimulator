from storyteller.interaction import CompletedInteraction, PendingInteraction

class Scenario:
    def __init__(self):
        self.completed_interactions = []
        self.pending_interaction = None
        self.ended = False
    
    def add_interaction(self, description, decision):
        interaction = CompletedInteraction(description, decision)
        self.completed_interactions.append(interaction)
        self.pending_interaction = None
    
    def end(self):
        self.ended = True
    
    def get_interactions_string(self):
        interactions_string = ""
        for interaction in self.completed_interactions:
            interactions_string += "Situation: "+interaction.description+" The user chose to "+interaction.decision + "\n"
        return interactions_string

    def set_pending_interaction(self, description, actions):
        self.pending_interaction = PendingInteraction(description, actions)
    
    def submit_action(self, action_index):
        description = self.pending_interaction.description
        action = self.pending_interaction.actions[action_index]
        self.add_interaction(description, action['action'])
        if action['exit_flag']:
            self.end()
    
    def submit_custom_action(self, action_desc):
        description = self.pending_interaction.description
        self.add_interaction(description, action_desc)
    
    def get_most_recent_action(self):
        if len(self.completed_interactions) > 0:
            return self.completed_interactions[len(self.completed_interactions)-1].decision
        else:
            return None
