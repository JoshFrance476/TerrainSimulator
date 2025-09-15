import config as config
import numpy as np

class DataProcessor:
    def __init__(self, world):
        self.world = world

    def generate_semantic_data(self, map_types, location):
        semantic_data = []
        for map_type in map_types:
            raw_vicinity_data = self.world.get_surrounding_data_map(location[0], location[1], 5, map_type)
            raw_adjacent_data = self.world.get_surrounding_data_map(location[0], location[1], 1, map_type)
            if map_type == "region":
                semantic_data.append("The region is " + config.REGION_RULES[self.world.get_cell_data(location)[0]["region"]]["name"])
                ids, counts = np.unique(raw_adjacent_data, return_counts=True)
                for id, count in zip(ids, counts):
                    region_name = config.REGION_RULES[id]["name"]
                    if count > 1:
                        semantic_data.append("It is adjacent to " + region_name)
                ids, counts = np.unique(raw_vicinity_data, return_counts=True)
                for id, count in zip(ids, counts):
                    region_name = config.REGION_RULES[id]["name"]
                    if count > 60:
                        semantic_data.append("Majority of the surrounding region is " + region_name)
                    elif count > 10:
                        semantic_data.append("There is some " + region_name + " region in the area")
                    elif count > 1:
                        semantic_data.append("There is a small " + region_name + " region in the area")
                    if region_name == "mountains":
                        semantic_data.append("There are mountains in the region")
            elif map_type == "resource":
                for resource in config.RESOURCE_RULES:
                    if resource in raw_vicinity_data:
                        semantic_data.append("There is " + resource + " in the area")


        return semantic_data


