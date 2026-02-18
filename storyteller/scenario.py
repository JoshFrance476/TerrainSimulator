from storyteller.interaction import CompletedInteraction, PendingInteraction

class Scenario:
    def __init__(self):
        self.completed_interactions = []
        self.pending_interaction = None
    
    def add_interaction(self, description, decision):
        interaction = CompletedInteraction(description, decision)
        self.completed_interactions.append(interaction)
    
    def get_interactions_string(self):
        interactions_string = ""
        for interaction in self.completed_interactions:
            interactions_string += interaction.description+", "+interaction.decision + "\n"
        return interactions_string

    def set_pending_interaction(self, description, actions):
        self.pending_interaction = PendingInteraction(description, actions)
    
    def sumbit_action(self, action_index):
        description = self.pending_interaction.description
        action = self.pending_interaction.actions[action_index]['action']
        self.add_interaction(description, action)
        self.pending_interaction = None