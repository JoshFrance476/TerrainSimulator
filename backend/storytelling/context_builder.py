class ContextBuilder:
    def __init__(self, state, world):
        self.state = state
        self.world = world
 
    def get_most_recent_movement_json(self):
        if len(self.state.movement_history) > 1:
            current_movement_entry = self.state.movement_history[-1]
            past_movement_entry = self.state.movement_history[-2]
            return {
                "direction": current_movement_entry["direction"],
                "from_biome": past_movement_entry["biome"],
                "to_biome": current_movement_entry["biome"]
            }
        return {}
    
    def get_chunk_context_json(self, cell):
        return self.world.get_chunk_context_json(cell)
 
    def build_scene_guide_context(self, selected_cell):
        tile = self.world.get_tile_data_json(selected_cell)
        return {
            "nearby_chunks": self.world.get_chunk_context_json(selected_cell),
            "current_tile": tile,
            "recent_movement": self.get_most_recent_movement_json(),
        }