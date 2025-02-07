from AnchorPoint import AnchorPoint
import config
import random
import numpy as np

class State():

    sid_counter = 1
    sid_map = np.zeros((config.ROWS, config.COLS), dtype=int)  # Territory ownership map

    def __init__(self, capital_location, name="Undefined"):
        self.name = name
        self.anchorpoints = [] # list of ap objects
        self.sid = State.sid_counter
        State.sid_counter += 1

        self.colour = self.assign_colour()

        self.create_anchor_point(capital_location)

        
    
    def create_anchor_point(self, location):
        new_ap = AnchorPoint(location, self.sid)

        self.anchorpoints.append(new_ap)
        
    
    def update_aps(self, sea_map, river_map, traversal_cost_map, population_map, id_map):

        for ap in self.anchorpoints:
            if len(ap.get_territory()) >= config.CITY_MAX_TERRITORY-30 and ap.can_expand:
                location_for_neighbour = ap.create_friendly_neighbour(self.sid, population_map, id_map, sea_map, river_map)
                self.create_anchor_point(location_for_neighbour)
            else:
                rng = random.randint(0, len(ap.get_territory()))
                if rng == 0:
                    ap.update_territory_size(sea_map, river_map, traversal_cost_map, population_map, id_map)
        self.sid_map = self.get_sid_territory_map()


    
    def assign_colour(self):
        """Assigns a unique color to state from the predefined list."""
        color = config.STATE_COLOUR_PALETTE[self.sid % len(config.STATE_COLOUR_PALETTE)]
        return color
    
    
    def get_apid_territory_map(self):
        territory_map = np.zeros((config.ROWS, config.COLS), dtype=int)
        for ap in self.anchorpoints:
            territory_list = ap.get_territory()
            for location in territory_list:
                territory_map[location] = ap.id
                if location == ap.get_location():
                    territory_map[location] = -1

        return territory_map

    def get_sid_territory_map(self):
        territory_map = np.zeros((config.ROWS, config.COLS), dtype=int)
        for ap in self.anchorpoints:
            territory_list = ap.get_territory()
            for location in territory_list:
                territory_map[location] = ap.sid
                if location == ap.get_location():
                    territory_map[location] = -1
        return territory_map    
  


