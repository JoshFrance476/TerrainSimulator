class CompletedInteraction:
    def __init__(self, description, decision, outcome):
        self.description = description
        self.decision = decision
        self.outcome = outcome

class PendingInteraction:
    def __init__(self, description, actions, outcomes):
        self.description = description
        self.action_table = {}

        if len(actions) != len(outcomes):
            print(actions, outcomes)
            raise ValueError("Error: Action count doesn't match outcome count.")
        
        
        for action, outcome in zip(actions, outcomes):
            self.action_table[action['action']] = {
                "exit_flag": action['exit_flag'],
                "outcome": outcome
                }
    