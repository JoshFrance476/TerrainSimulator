class Storyline:
    def __init__(self, overview, location, scope):
        self.overview = overview
        self.location = location
        self.scope = scope
        self.events = []
    
    def add_event(self, event):
        self.events.append(event)