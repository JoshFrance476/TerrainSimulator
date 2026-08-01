from storytelling.interaction import Interaction

class Scene:
    def __init__(self):
        self.interactions = []
        self.ended = False

    @property
    def pending_interaction(self):
        last = self.interactions[-1] if self.interactions else None
        return last if last and not last.is_complete else None

    @property
    def completed_interactions(self):
        return [i for i in self.interactions if i.is_complete]
    
    def end_scene(self):
        self.ended = True
    
    def get_interactions(self):
        interactions = []
        for interaction in self.completed_interactions:
            interactions.append({"Situation": interaction.description,
                                 "Action": interaction.chosen_action})
        return interactions

    def add_interaction(self, description, actions, outcomes, guide):
        if self.pending_interaction:
            self.interactions.remove(self.pending_interaction)
        self.interactions.append(Interaction(description, actions, outcomes, guide))
    
    def submit_action(self, action):
        interaction = self.pending_interaction
        interaction.set_chosen_action(action)
        if interaction.ends_scene():
            self.end_scene()

    def to_dict(self):
        return {
            "interactions": [i.to_dict() for i in self.interactions],
            "ended": self.ended,
        }

    def get_history(self):
        history = []
        for interaction in self.interactions:
            history.append({ 
                "description": interaction.description,
                "chosen_action": interaction.chosen_action,
                "outcome": interaction.outcome
            })
        return history
                
    