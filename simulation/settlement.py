import numpy as np
from utils.config import RESOURCE_NAMES, RESOURCE_RULES, REGION_NAME_TO_ID, REGION_RULES
from dataclasses import dataclass


@dataclass
class Resource:
    name: str
    location: tuple[int, int]
    distance: int
    collected: bool = False



class Settlement:

    def __init__(self, id, name, r, c, world):
        self.id = id
        self.name = name
        self.description = ""
        self.r = r
        self.c = c
        self._world = world

        self.reach = 3

        self.available_resources = self.get_available_resources()
        self.improved_resources = []
        self.population_capacity *= 5

        self.growth_rate = 1.02
        self.cohesion = 1
        

        self.thresholds = [5, 10, 15, 20, 25]
        self.triggered_thresholds = set()

        if self.population < 1:
            self.population = 1
        
        self._world.set_map_data_at("colour", (self.r, self.c), (0, 0, 0))

        self._world.event_manager.generate_event_with_probability("settlement founded", (self.r, self.c), {"name": name}, 0.1)
        
    
    def update(self):
        self.population *= self.growth_rate

        for i, threshold in enumerate(self.thresholds):
            if self.population > threshold and i not in self.triggered_thresholds:
                self.triggered_thresholds.add(i)
                self.improve_tile()
                self._world.event_manager.generate_event_with_probability("settlement growth", (self.r, self.c), {"name": self.name, "population": f"{self.population*1000:.0f}"}, 0.1)


    def get_available_resources(self):
        available_resources = []
        resource_map = self._world.get_surrounding_data_map(self.r, self.c, self.reach, map="resource")

        masked_resource_map = np.argwhere(resource_map != 0)


        for dr, dc in masked_resource_map:
            r = self.r + dr - self.reach
            c = self.c + dc - self.reach

            distance = abs(r - self.r) + abs(c - self.c)

            available_resources.append(Resource(RESOURCE_NAMES[resource_map[dr, dc]], (r, c), distance))

        return available_resources


    
    
    def improve_tile(self):
        furthest_distance = self.reach*2
        resource_to_improve = None
        for resource in self.available_resources:
            if resource.distance < furthest_distance and resource.collected == False:
                furthest_distance = resource.distance
                resource_to_improve = resource

        if resource_to_improve:
            resource_to_improve.collected = True

            if "upgraded_bonuses" in RESOURCE_RULES[resource_to_improve.name]:
                self.growth_rate += RESOURCE_RULES[resource_to_improve.name]["upgraded_bonuses"]["population_growth"]
            
            self._world.set_map_data_at("region", resource_to_improve.location, REGION_NAME_TO_ID[RESOURCE_RULES[resource_to_improve.name]["upgraded"]])
            if "colour" in REGION_RULES[REGION_NAME_TO_ID[RESOURCE_RULES[resource_to_improve.name]["upgraded"]]]:
                self._world.set_map_data_at("colour", resource_to_improve.location, REGION_RULES[REGION_NAME_TO_ID[RESOURCE_RULES[resource_to_improve.name]["upgraded"]]]["colour"])
            self.improved_resources.append(resource_to_improve)
            self.available_resources.remove(resource_to_improve)


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
