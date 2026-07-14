class Interaction:
    def __init__(self, description, actions, outcomes, guide):
        self.description = description
        self.action_table = {}
        self.chosen_action = None
        self.outcome = None
        self.guide = guide
    
        if len(actions) != len(outcomes):
            print(actions, outcomes)
            raise ValueError("Error: Action count doesn't match outcome count.")
        
        for action, outcome in zip(actions, outcomes):
            self.action_table[action['action']] = {
                "exit_flag": action['exit_flag'],
                "outcome": outcome
                }
    
    def set_chosen_action(self, chosen_action):
        self.chosen_action = chosen_action
        self.outcome = self.action_table[chosen_action]["outcome"]
    
    
    def ends_scene(self):
        return self.action_table[self.chosen_action]["exit_flag"]