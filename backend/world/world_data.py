from generation.generator_main import generate_data_maps, update_stage_3, update_steepness, update_biome

class WorldData:
    def __init__(self, rows, cols, biome_config, world_data=None):
        self.rows, self.cols = rows, cols
        self.biome_config = biome_config
        if world_data:
            self.world_data = world_data
            self.update_stage_3()
        else:
            self.world_data = generate_data_maps(self.rows, self.cols, self.biome_config)
    

    def get_cell_data(self, pos):
        r, c = pos

        cell_data = {}
        
        for map in self.world_data:
            cell_data[map] = self.world_data[map][r, c]

        return cell_data

    def get_world_data(self):
        return self.world_data
    
    def get_biome_data(self, x0, y0, x1, y1):
        biome_data = {}

        for map in self.world_data:
            biome_data[map] = self.world_data[map][y0:y1, x0:x1]

        return biome_data
    
    def set_map_data(self, map_name, data):
        self.world_data[map_name][:] = data
    
    def set_map_data_at(self, map_name, pos, data):
        self.world_data[map_name][pos] = data
    
    def set_biome_with_mask(self, mask, data):
        self.world_data["biome"][mask] = data
        elevation = self.world_data["elevation"]
        if data == 0:
            elevation[mask & (elevation > self.biome_config.get_sea_level())] = 0
        else:
            elevation[mask & (elevation < self.biome_config.get_sea_level())] = 0.001
    
    def get_biome_name_from_id(self, bid):
        return self.biome_config.get_biome_name_from_id(bid)
    
    def get_biome_at(self, location):
        return self.biome_config.biomes[self.world_data["biome"][location]]["name"].title()
    
    def update_biome(self, mask):
        if mask is not None:
            self.world_data["biome"] = update_biome(self.world_data["elevation"],
                                                        self.world_data["temperature"],
                                                        self.world_data["rainfall"],
                                                        self.world_data["sea_proximity"],
                                                        self.world_data["river_proximity"],
                                                        self.biome_config,
                                                        mask,
                                                        self.world_data["biome"])
        else:
            self.world_data["biome"] = update_biome(self.world_data["elevation"],
                                                        self.world_data["temperature"],
                                                        self.world_data["rainfall"],
                                                        self.world_data["sea_proximity"],
                                                        self.world_data["river_proximity"],
                                                        self.biome_config)

    def update_stage_3(self):
        new_trav_map, new_colour_map = update_stage_3(self.world_data["elevation"],
                                                    self.world_data["biome"],
                                                    self.world_data["steepness"],
                                                    self.biome_config)
        self.world_data["colour"] = new_colour_map
        self.world_data["traversal_cost"] = new_trav_map
    
    def update_steepness(self):
        self.world_data['steepness'] = update_steepness(self.world_data['elevation'])
        
