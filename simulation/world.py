from worldData import WorldData

class World:
    """Handles simulator and high level world logic."""

    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.data = WorldData(rows, cols)
    
    def step(self):
        self.data.update()

    #def update(self):
        #self.dynamic_maps = update_dynamic_maps(self.static_maps_dict, self.dynamic_maps_dict)








    


