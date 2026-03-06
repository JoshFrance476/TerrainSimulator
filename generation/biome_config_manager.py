import json
import numpy as np
import colorsys

class BiomeConfigManager:
    def __init__(self):

        self.biomes = {}
        self.constants = {}

        self.name_to_id = {}
        self.by_name = {}
        self.colour_lookup = {}
        self.cost_lookup = {}

    
    def load_biome_config_file(self, biome_config_file):         
        self.constants = biome_config_file.get("constants", {})
        biomes = biome_config_file["biomes"]

        self.biomes = self.resolve_constants(biomes, self.constants)
        self.update_lookups()
    
    
    def add_biome(self, name, h, s, v, traversal_cost):
        new_biome = {
            "name": name,
            "colour": {"h": h, "s": s, "v": v},
            "base_traversal_cost": traversal_cost
        }
        self.biomes.append(new_biome)
        self.update_lookups()
    
    def edit_biome(self, index, name, h, s, v, traversal_cost):
        biome_to_edit = self.biomes[index]
        biome_to_edit["name"] = name
        biome_to_edit["colour"]["h"] = h
        biome_to_edit["colour"]["s"] = s
        biome_to_edit["colour"]["v"] = v
        biome_to_edit["base_traversal_cost"] = traversal_cost
        self.update_lookups()
    
    def update_lookups(self):
        self.name_to_id = {r["name"]: idx for idx, r in enumerate(self.biomes)}

        self.by_name = {r["name"]: r for r in self.biomes}

        self.colour_lookup = np.asarray(
            [(r["colour"]["h"], r["colour"]["s"], r["colour"]["v"]) for r in self.biomes],
            dtype=np.float32
        )  # shape (N, 3)

        self.cost_lookup = np.array(
            [r["base_traversal_cost"] for r in self.biomes],
            dtype=np.float32
        )

    def get_starting_location(self):
        return self.constants['STARTING_LOCATION'][0], self.constants['STARTING_LOCATION'][1]

    def set_starting_location(self, location):
        self.constants['STARTING_LOCATION'] = [location[0], location[1]]
    
    def resolve_constants(self, obj, constants):
        if isinstance(obj, dict):
            return {
                k: self.resolve_constants(
                    constants.get(v, v) if isinstance(v, str) else v,
                    constants
                )
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [self.resolve_constants(v, constants) for v in obj]
        return obj

    def get_sea_level(self):
        return self.constants["SEA_LEVEL"]