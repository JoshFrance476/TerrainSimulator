class CompletedInteraction:
    def __init__(self, description, decision):
        self.description = description
        self.decision = decision

class PendingInteraction:
    def __init__(self, description, actions):
        self.description = description
        self.actions = actions
    