class Settlement:

    def __init__(self, id, name, r, c, population_array):
        self.id = id
        self.name = name
        self.r = r
        self.c = c
        self._population_array = population_array   #Pointer to population map in worldData. Means 'population' is linked to worldData

    #def update(self):
        #self.population *= 1.01
    
    @property
    def population(self):
        return self._population_array[self.r, self.c]
    
    @population.setter
    def population(self, value):
        self._population_array[self.r, self.c] = value
