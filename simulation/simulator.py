from simulation.state_manager import StateManager
from overlays.overlay_generator import generate_territory_overlay
from utils.colour_utils import generate_color_map
from generation.generator_main import generate_static_maps, generate_dynamic_maps, update_dynamic_maps



class Simulator:
    def __init__(self):
        self.static_maps = generate_static_maps()
        self.dynamic_maps = generate_dynamic_maps(self.static_maps)

        self.step_counter = 0

        self.colour_map = generate_color_map(self.static_maps, True, True)
        self.state_manager = StateManager(self.dynamic_maps["population_map"])
        self.display_map = self.colour_map
        self.selected_cell = (0, 0)


    def update(self):
        self.dynamic_maps = update_dynamic_maps(self.static_maps, self.dynamic_maps)
        self.state_manager.update_states(self.static_maps["sea_map"], self.static_maps["river_map"], self.static_maps["traversal_cost_map"], self.dynamic_maps["population_map"])
        self.display_map = generate_territory_overlay(
            self.colour_map,
            self.state_manager.get_global_sid_territory_map(),
            self.state_manager.states
        )
        self.step_counter += 1

    def get_step_counter(self):
        return self.step_counter

    def get_display_map(self):
        return self.display_map


    def get_static_maps(self):
        return self.static_maps

    def get_dynamic_maps(self):
        return self.dynamic_maps



    


