from llm_api import ask_deepseek, desc_schema


class Settlement:

    def __init__(self, id, name, r, c, world_data):
        self.id = id
        self.name = name
        self.description = ""
        self.r = r
        self.c = c
        self._world_data = world_data   #Pointer to worldData. Means settlement data is linked directly to map data
    
    #def update(self):
        #self.population *= 1.01

    def generate_description(self):
        prompt = f"""Task:
        Write a short, one-sentence description of this settlement based on the context. 
        Context: Name: {self.name}, Row: {self.r}, Col: {self.c}, Population: {self.population}, Region: {self._world_data['region'][self.r, self.c]}
        """
        self.description = ask_deepseek(prompt, desc_schema)
    
    
    #Map-linked values
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
