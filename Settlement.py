from llm_api import ask_deepseek, desc_schema


class Settlement:

    def __init__(self, id, name, r, c, world_data):
        self.id = id
        self.name = name
        self.description = ""
        self.r = r
        self.c = c
        self._world_data = world_data   #Pointer to worldData. Means settlement data is linked directly to map data

        self.population_capacity *= 5

        self.growth_rate = 1.01
        self.cohesion = 1
        
    
    def update(self):
        self.population *= self.growth_rate

    
    
    
    #Map-linked values
    @property
    def population_capacity(self):
        return self._world_data["population_capacity"][self.r, self.c]
    
    @population_capacity.setter
    def population_capacity(self, value):
        self._world_data["population_capacity"][self.r, self.c] = value
    
    @property
    def fertility(self):
        return self._world_data["fertility"][self.r, self.c]
    
    @property
    def region(self):
        return self._world_data["region"][self.r, self.c]
    
    @property
    def rainfall(self):
        return self._world_data["rainfall"][self.r, self.c]
    
    @property
    def temperature(self):
        return self._world_data["temperature"][self.r, self.c]
    
    @property
    def population(self):
        return self._world_data["population"][self.r, self.c]
    
    @population.setter
    def population(self, value):
        self._world_data["population"][self.r, self.c] = value
