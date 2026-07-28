class Interaction:
    def __init__(self, description, actions, outcomes, guide):
        self.description = description
        self.action_table = []
        self.chosen_action = None
        self.outcome = None
        self.guide = guide
        
        for action, outcome in zip(actions, outcomes):
            self.action_table.append({
                "action": action['action'],
                "exit_flag": action['exit_flag'],
                "outcome": outcome
            })

    @property
    def is_complete(self):
        return self.chosen_action is not None
    
    def set_chosen_action(self, chosen_action):
        self.chosen_action = chosen_action
        self.outcome = next(a["outcome"] for a in self.action_table if a["action"] == chosen_action)
    
    def ends_scene(self):
        return next(a["exit_flag"] for a in self.action_table if a["action"] == self.chosen_action)

    def to_dict(self):
        return {
            "description": self.description,
            "guide": self.guide,
            "chosen_action": self.chosen_action,
            "outcome": self.outcome,
            "completed": self.is_complete,
            "actions": [
                {"action": a["action"], "exit_flag": a["exit_flag"]}
                for a in self.action_table
            ]
        }