from storytelling.interaction import CompletedInteraction, PendingInteraction

class Scenario:
    def __init__(self, focus="", environment="", scene_significance=""):
        self.completed_interactions = []
        self.pending_interaction = None
        self.ended = False
        self.focus = focus
        self.environment = environment
        self.significance = scene_significance
        self.interaction_count = 0
    
    def add_interaction(self, description, decision):
        interaction = CompletedInteraction(description, decision)
        self.completed_interactions.append(interaction)
        self.interaction_count += 1
        self.pending_interaction = None
    
    def end(self):
        self.ended = True
    
    def get_interactions_json(self):
        interactions = []
        for interaction in self.completed_interactions:
            interactions.append({"Situation": interaction.description,
                                 "Action": interaction.decision})
        return interactions

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
