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
            if map_type == "biome":
                semantic_data.append("The biome is " + config.BIOME_RULES[self.world.get_cell_data(location)[0]["biome"]]["name"])
                ids, counts = np.unique(raw_adjacent_data, return_counts=True)
                for id, count in zip(ids, counts):
                    biome_name = config.BIOME_RULES[id]["name"]
                    if count > 1:
                        semantic_data.append("It is adjacent to " + biome_name)
                ids, counts = np.unique(raw_vicinity_data, return_counts=True)
                for id, count in zip(ids, counts):
                    biome_name = config.BIOME_RULES[id]["name"]
                    if count > 60:
                        semantic_data.append("Majority of the surrounding biome is " + biome_name)
                    elif count > 10:
                        semantic_data.append("There is some " + biome_name + " biome in the area")
                    elif count > 1:
                        semantic_data.append("There is a small " + biome_name + " biome in the area")
                    if biome_name == "mountains":
                        semantic_data.append("There are mountains in the biome")
        return semantic_data


