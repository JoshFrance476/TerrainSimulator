from story_generation.interaction import Interaction

class Scene:
    def __init__(self):
        self.guide = None
        self.interactions = []
        self.ended = False
        self.summary = None

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

    def add_interaction(self, description, actions):
        if self.pending_interaction:
            self.interactions.remove(self.pending_interaction)
        self.interactions.append(Interaction(description, actions))
    
    def submit_action(self, action):
        interaction = self.pending_interaction
        interaction.set_chosen_action(action)
        if interaction.ends_scene():
            self.end_scene()

    def to_dict(self):
        return {
            "guide": self.guide,
            "interactions": [i.to_dict() for i in self.interactions],
            "ended": self.ended,
        }

    def get_history(self):
        history = []
        for interaction in self.interactions:
            if interaction.is_complete:
                history.append({ 
                    "description": interaction.description,
                    "chosen_action": interaction.chosen_action,
                })
        return history

    def set_guide(self, guide):
        self.guide = guide
                
    