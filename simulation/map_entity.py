class MapEntity:
    def __init__(self, location):
        self.location = location
    
    def set_location(self, new_location):
        self.location = new_location
    
    def get_location(self):
        return self.location