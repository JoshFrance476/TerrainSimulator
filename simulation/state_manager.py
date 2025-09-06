from simulation.state import State

class StateManager:
    def __init__(self, world):
        self._world = world

        self.states = {}

        self.next_state_id = 0
    
    def update(self):
        for s in self._world.find_eligible_state_founders():
            self.create_state(s.name, s.r, s.c)

    
    def create_state(self, name, r, c):
        new_state = State(self.next_state_id, name)
        self.next_state_id += 1

        self.state_map[r, c] = new_state.id

        self.states[new_state.id] = new_state

        return new_state

    @property
    def state_map(self):
        return self._world.get_map_data("state")
    
    @state_map.setter
    def state_map(self, value):
        self._world.set_map_data("state", value)
    
    


