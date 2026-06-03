from storytelling.interaction import CompletedInteraction, PendingInteraction

class Scenario:
    def __init__(self, guide=""):
        self.completed_interactions = []
        self.pending_interaction = None
        self.ended = False
        self.guide = guide
        self.interaction_count = 0
    
    def add_interaction(self, description, action, outcome):
        interaction = CompletedInteraction(description, action, outcome)
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

    def set_pending_interaction(self, description, actions, outcomes):
        self.pending_interaction = PendingInteraction(description, actions, outcomes)
    
    def submit_action(self, action):
        description = self.pending_interaction.description
        outcome = self.pending_interaction.action_table[action]["outcome"]
        if self.pending_interaction.action_table[action]["exit_flag"]:
            self.end()
        self.add_interaction(description, action, outcome)
    
    def submit_custom_action(self, action_desc):
        description = self.pending_interaction.description
        self.add_interaction(description, action_desc)
    
    def get_most_recent_action(self):
        if len(self.completed_interactions) > 0:
            return self.completed_interactions[len(self.completed_interactions)-1].decision
        else:
            return None
    
    def get_most_recent_outcome(self):
        if len(self.completed_interactions) > 0:
            return self.completed_interactions[len(self.completed_interactions)-1].outcome
        else:
            return None

    def get_outcomes(self):
        outcome_list = []
        for interaction in self.completed_interactions:
            outcome_list.append(interaction.outcome)
        return outcome_list[::-1]