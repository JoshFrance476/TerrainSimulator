class Interaction:
    def __init__(self, description, actions):
        self.description = description
        self.action_table = []
        self.chosen_action = None
        
        for action in actions:
            self.action_table.append({
                "action": action['action'],
                "exit_flag": action['exit_flag'],
            })

    @property
    def is_complete(self):
        return self.chosen_action is not None
    
    def set_chosen_action(self, chosen_action):
        self.chosen_action = chosen_action
    
    def ends_scene(self):
        return next(a["exit_flag"] for a in self.action_table if a["action"] == self.chosen_action)

    def to_dict(self):
        return {
            "description": self.description,
            "chosen_action": self.chosen_action,
            "completed": self.is_complete,
            "actions": [
                {"action": a["action"], "exit_flag": a["exit_flag"]}
                for a in self.action_table
            ]
        }