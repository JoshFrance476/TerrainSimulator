class Settlement:

    def __init__(self, id, name, r, c, world, resources = []):
        self.id = id
        self.name = name
        self.description = ""
        self.r = r
        self.c = c
        self._world = world

        self.resources = resources

        self.population_capacity *= 5

        self.growth_rate = 1.01
        self.cohesion = 1
        
    
    def update(self):
        self.population *= self.growth_rate
    

    #Map-linked values

    @property
    def population_capacity(self):
        return self._world.get_map_data("population_capacity")[self.r, self.c]
    
    @population_capacity.setter
    def population_capacity(self, value):
        self._world.get_map_data("population_capacity")[self.r, self.c] = value
    
    @property
    def fertility(self):
        return self._world.get_map_data("fertility")[self.r, self.c]
    
    @property
    def state(self):
        return self._world.get_map_data("state")[self.r, self.c]
    
    @property
    def region(self):
        return self._world.get_map_data("region")[self.r, self.c]
    
    @property
    def rainfall(self):
        return self._world.get_map_data("rainfall")[self.r, self.c]
    
    @property
    def temperature(self):
        return self._world.get_map_data("temperature")[self.r, self.c]
    
    @property
    def population(self):
        return self._world.get_map_data("population")[self.r, self.c]
    
    @population.setter
    def population(self, value):
        self._world.get_map_data("population")[self.r, self.c] = value
