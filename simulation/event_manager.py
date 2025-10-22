from simulation.event import Event

class EventManager:
    def __init__(self, world):
        self.event_log = []
        self.world = world
    
    def add_event(self, type, location, description):
        tick_count = self.world.tick_count
        new_event = Event(type, location, tick_count, description)
        self.event_log.append(new_event)
        return new_event

    def get_event_log(self):
        return self.event_log
    
    def filter_event_log_by_tick(self, tick_count):
        return [event for event in self.event_log if event.tick_count == tick_count]
    
    def filter_event_log_by_event_type(self, event_type):
        return [event for event in self.event_log if event.event_type == event_type]
    
    def filter_event_log_by_location(self, location):
        return [event for event in self.event_log if event.location == location]
    
    def get_event_log_by_vicinity(self, location, radius):
        events = []
        for event in self.event_log:
            if event.location[0] in range(location[0] - radius, location[0] + radius) and event.location[1] in range(location[1] - radius, location[1] + radius):
                events.append(event)
        return events
    