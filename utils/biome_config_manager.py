import json
import numpy as np
import colorsys

class BiomeConfigManager:
    def __init__(self):
        self.config = {}
        self.name_to_id = {}
        self.by_name = {}
        self.colour_lookup = {}
        self.cost_lookup = {}

        self.constants = {}
    
    def load_biome_config_file(self, file_name):
        with open(file_name, "r") as f:
            biome_config_file = json.load(f)
            
        BIOME_CONSTANTS = biome_config_file.get("constants", {})
        BIOME_RULES = biome_config_file["biomes"]

        self.config = self.resolve_constants(BIOME_RULES, BIOME_CONSTANTS)

        self.constants = BIOME_CONSTANTS

        self.update_lookups()
    
    def add_biome(self, name, h, s, v, traversal_cost):
        new_biome = {
            "name": name,
            "colour": {"h": h, "s": s, "v": v},
            "base_traversal_cost": traversal_cost
        }
        self.config.append(new_biome)
        self.update_lookups()
    
    def edit_biome(self, index, name, h, s, v, traversal_cost):
        biome_to_edit = self.config[index]
        biome_to_edit["name"] = name
        biome_to_edit["colour"]["h"] = h
        biome_to_edit["colour"]["s"] = s
        biome_to_edit["colour"]["v"] = v
        biome_to_edit["base_traversal_cost"] = traversal_cost
        self.update_lookups()
    
    def update_lookups(self):
        self.name_to_id = {r["name"]: idx for idx, r in enumerate(self.config)}

        self.by_name = {r["name"]: r for r in self.config}

        self.colour_lookup = np.asarray(
            [(r["colour"]["h"], r["colour"]["s"], r["colour"]["v"]) for r in self.config],
            dtype=np.float32
        )  # shape (N, 3)

        self.cost_lookup = np.array(
            [r["base_traversal_cost"] for r in self.config],
            dtype=np.float32
        )

    
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
