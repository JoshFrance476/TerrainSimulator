class Event:
    def __init__(self, event_type, location, tick_count, description):
        self.event_type = event_type
        self.location = location
        self.tick_count = tick_count
        self.description = description
        self.narrative = ""
    
    def add_event_narrative(self, narrative):
        self.narrative = narrative