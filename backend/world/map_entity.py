class MapEntity:
    def __init__(self, location, boundary):
        self.location = location
        self.boundary = boundary
    
    def set_location(self, new_location):
        self.location = new_location
    
    def get_location(self):
        return self.location
    
    def move_north(self):
        new_location = (self.location[0]-1, self.location[1])
        if self.within_boundary(new_location):
            self.location = new_location
    
    def move_east(self):
        new_location = (self.location[0], self.location[1]+1)
        if self.within_boundary(new_location):
            self.location = new_location
    
    def move_south(self):
        new_location = (self.location[0]+1, self.location[1])
        if self.within_boundary(new_location):
            self.location = new_location
    
    def move_west(self):
        new_location = (self.location[0], self.location[1]-1)
        if self.within_boundary(new_location):
            self.location = new_location
    
    def within_boundary(self, location):
        return 0 <= location[0] < self.boundary[0] and 0 <= location[1] < self.boundary[1]