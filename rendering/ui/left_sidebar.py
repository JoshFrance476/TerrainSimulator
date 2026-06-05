import pygame
import config
from rendering.ui.widgets.textbox import TextBox
from rendering.ui.widgets.label import Label
from rendering.ui.widgets.button import Button
from rendering.ui.widgets.slider import Slider
from rendering.ui.widgets.colour_preview import ColourPreview
from rendering.ui.widgets.component_container import ComponentContainer
from rendering.ui.widgets.container_list import ContainerList
from rendering.ui.widgets.line_divider import LineDivider
from app.app_state import LeftPage

class LeftSidebarController:
    def __init__(self, fonts, state, world, interaction_system, storyteller):
        self.state = state
        self.world = world
        self.fonts = fonts
        self.component_list = []

        self.interaction_system = interaction_system
        self.storyteller = storyteller

        self.navigation_bar = [[Button(65,20, lambda: setattr(self.state, "left_page", LeftPage.BIOME_EDITOR), "Biome", self.fonts.small_font),
                                Button(85,20, lambda: setattr(self.state, "left_page", LeftPage.VIEW_CHARACTER), "Character", self.fonts.small_font),
                                Button(85,20, lambda: setattr(self.state, "show_menu", True), "Menu", self.fonts.small_font)],
                                LineDivider(config.SIDEBAR_WIDTH, thickness=0, top_padding=10, bottom_padding=5)]

    def show_page(self, page_name):
        match page_name:
            case LeftPage.VIEW_CHARACTER:
                self.show_character_page()
            case LeftPage.BIOME_EDITOR:
                self.show_biome_manager_page()
            case LeftPage.REGION_EDITOR:
                self.show_region_setup_page(self.state.active_region_edit_id)
            case LeftPage.VIEW_LOCATION:
                self.show_location_info_page()
            case LeftPage.TILE_EDITOR:
                self.show_tile_manager_page(self.state.active_biome_edit_id)
        
    def show_character_page(self):
        self.clear_page()
        self.component_list.extend(self.navigation_bar)

        title_label = Label("Your Character", self.fonts.header)
        self.component_list.append(title_label)

        character_notebook = self.storyteller.get_notebook()

        for bulletpoint in character_notebook:
            self.component_list.append(Label(bulletpoint, self.fonts.small_font))
        
        history_label = Label("History", self.fonts.large_font)
        self.component_list.append(history_label)

        character_history = self.storyteller.get_character_history()

        for bulletpoint in character_history:
            self.component_list.append(Label(bulletpoint, self.fonts.small_font))

    def show_region_setup_page(self, region_id):
        self.clear_page()

        region = self.world.get_region(region_id)
        self.component_list.append(Label("Add Region", self.fonts.header))
        self.component_list.append(Label("Title:", self.fonts.small_font))
        self.component_list.append(TextBox(self.interaction_system, self.fonts.small_font, 220, 25, default_text=region.title))
        self.component_list.append(Label("Visible Description:", self.fonts.small_font))
        self.component_list.append(TextBox(self.interaction_system, self.fonts.small_font, 220, 25, default_text=region.visible_desc))
        self.component_list.append(Label("Hidden Description:", self.fonts.small_font))
        self.component_list.append(TextBox(self.interaction_system, self.fonts.small_font, 220, 25, default_text=region.hidden_desc))
        self.component_list.append(Button(50, 25, lambda: self.interaction_system.set_region_info(self.component_list[2].text, self.component_list[4].text, self.component_list[6].text, region_id=region_id), "Submit", self.fonts.small_font))
    
    def show_tile_manager_page(self, biome_index = -1):
        self.clear_page()

        if biome_index != -1:
            biome_info = self.world.get_biome_data_from_id(biome_index)
            tile_name = TextBox(self.interaction_system, self.fonts.small_font, 150, 20, biome_info["name"])
            tile_desc = TextBox(self.interaction_system, self.fonts.small_font, 150, 20, biome_info["description"])
            tile_trav_cost = TextBox(self.interaction_system, self.fonts.small_font, 150, 20, str(biome_info["base_traversal_cost"]))
            hue_slider = Slider(self.fonts.small_font, 0, 360, config.SIDEBAR_WIDTH - 120, biome_info["colour"]["h"], top_padding=2)
            sat_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, biome_info["colour"]["s"]*100, top_padding=2)
            val_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, biome_info["colour"]["v"]*100, top_padding=2)
            submit_button = Button(50, 25, lambda: self.interaction_system.edit_biome(biome_index, tile_name.text, hue_slider.value, sat_slider.value/100, val_slider.value/100, float(tile_trav_cost.text), tile_desc.text), "Submit", self.fonts.small_font)
        else:
            tile_name = TextBox(self.interaction_system, self.fonts.small_font, 150, 20)
            tile_desc = TextBox(self.interaction_system, self.fonts.small_font, 150, 20)
            tile_trav_cost = TextBox(self.interaction_system, self.fonts.small_font, 150, 20, "0") 
            hue_slider = Slider(self.fonts.small_font, 0, 360, config.SIDEBAR_WIDTH - 120, top_padding=2)
            sat_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, 100, top_padding=2)
            val_slider = Slider(self.fonts.small_font, 0, 100, config.SIDEBAR_WIDTH - 120, 100, top_padding=2)
            submit_button = Button(50, 25, lambda: self.interaction_system.add_biome(tile_name.text, hue_slider.value, sat_slider.value/100, val_slider.value/100, float(tile_trav_cost.text), tile_desc.text),"Submit", self.fonts.small_font)

        self.component_list.append(
            Label("Tile Manager", self.fonts.header)
        )

        self.component_list.append(ColourPreview(50, 50, hue_slider, sat_slider, val_slider))

        self.component_list.append(Label("Tile name:", self.fonts.large_font))
        self.component_list.append(tile_name)

        self.component_list.append(Label("Tile Description:", self.fonts.large_font))
        self.component_list.append(tile_desc)

        self.component_list.append(Label("Traversal Cost:", self.fonts.large_font))
        self.component_list.append(tile_trav_cost)

        self.component_list.append(Label("Colour:", self.fonts.large_font))

        self.component_list.append(Label("Hue:", self.fonts.small_font, top_padding=2))
        self.component_list.append(hue_slider)

        self.component_list.append(Label("Saturation:", self.fonts.small_font, top_padding=2))
        self.component_list.append(sat_slider)

        self.component_list.append(Label("Value:", self.fonts.small_font, top_padding=2))
        self.component_list.append(val_slider)

        self.component_list.append(submit_button)

        
    def show_biome_manager_page(self):
        self.clear_page()
        self.component_list.extend(self.navigation_bar)
        self.component_list.append(Label("Biome Manager", self.fonts.header))
        biome_container_list = ContainerList(config.SIDEBAR_WIDTH-10, 800)
        for index, biome in enumerate(self.world.get_biomes()):
            biome_container = ComponentContainer(True)
            biome_container.add_component(Label(biome["name"].capitalize(), self.fonts.large_font, left_padding=5, top_padding=5))
            biome_container.add_component([ColourPreview(20, 20, biome["colour"]["h"], biome["colour"]["s"], biome["colour"]["v"]),
                                        Button(50, 20, lambda i = index: (setattr(self.state, "active_biome_edit_id", i),
                                                                          setattr(self.state, "left_page", LeftPage.TILE_EDITOR)), "Edit", self.fonts.small_font, left_padding=5),
                                        Button(50, 20, lambda i = index: self.interaction_system.toggle_tile_paint(i), "Paint", self.fonts.small_font, left_padding=5)])
            biome_container_list.add_container(biome_container)
        
        self.component_list.append(biome_container_list)
        self.component_list.append(LineDivider(config.SIDEBAR_WIDTH, thickness=0, top_padding=10))
        self.component_list.append(Button(100, 20, lambda: (setattr(self.state, "active_biome_edit_id", -1),
                                                            setattr(self.state, "left_page", LeftPage.TILE_EDITOR)), "Add Region", self.fonts.small_font))
    
    def show_location_info_page(self):
        self.clear_page()

        title_label = Label("Location", self.fonts.header, config.SIDEBAR_WIDTH)

        self.component_list.extend(self.navigation_bar)
        self.component_list.append(title_label)
        
        if self.state.selected_cell:
            biome_data = self.world.get_biome_data_at_location(self.state.selected_cell)
            biome_name_label = Label(biome_data["name"].title(), self.fonts.large_font, top_padding=2)
            biome_description_label = Label(biome_data["description"], self.fonts.small_font, top_padding=2)
            self.component_list.append(biome_name_label)
            self.component_list.append(biome_description_label)
            if self.state.debug_mode:
                cell_data = self.world.get_cell_data(self.state.selected_cell)
                elevation_label = Label(f"Elevation: {cell_data['elevation']}", self.fonts.small_font)
                temperature_label = Label(f"Temperature: {cell_data['temperature']}", self.fonts.small_font)
                rainfall_label = Label(f"Rainfall: {cell_data['rainfall']}", self.fonts.small_font)
                steepness_label = Label(f"Steepness: {cell_data['steepness']}", self.fonts.small_font)
                traversal_cost_label = Label(f"Traversal Cost: {cell_data['traversal_cost']}", self.fonts.small_font)
                chunk_id_label = Label(f"Chunk ID: {self.world.get_chunk_id_at(self.state.selected_cell)}", self.fonts.small_font)

                self.component_list.append(elevation_label)
                self.component_list.append(temperature_label)
                self.component_list.append(rainfall_label)
                self.component_list.append(steepness_label)
                self.component_list.append(traversal_cost_label)
                self.component_list.append(chunk_id_label)

                current_scenario_data = self.storyteller.get_current_scenario_debug_info()

                if current_scenario_data:
                    scenario_focus_label = Label(f"Scene focus: {current_scenario_data['focus']}", self.fonts.small_font)
                    scenario_environment_label = Label(f"Scene environment: {current_scenario_data['environment']}", self.fonts.small_font)
                    scenario_significance_label = Label(f"Scene significance: {current_scenario_data['significance']}", self.fonts.small_font)
                    self.component_list.append(scenario_focus_label)
                    self.component_list.append(scenario_environment_label)
                    self.component_list.append(scenario_significance_label)

                local_chunks_dict = self.world.get_closest_chunks(self.state.selected_cell)
                for chunk in local_chunks_dict:
                    self.component_list.append(Label(f"Local Chunk: {chunk['id']} {chunk['biome']}, {chunk['distance']}, {chunk['direction']}", self.fonts.small_font))
                
        else:
            self.component_list.append(Label("No tile selected", self.fonts.large_font, top_padding=2))
        
        self.component_list.append(LineDivider(config.SIDEBAR_WIDTH, 2))
        

        for region in self.world.get_regions_at_location(self.state.selected_cell):
            if region.title:
                self.component_list.append(Label(region.title, self.fonts.large_font))
            if region.visible_desc:
                self.component_list.append(Label(region.visible_desc, self.fonts.small_font))
            if region.hidden_desc:
                self.component_list.append(Label(region.hidden_desc, self.fonts.small_font))
            self.component_list.append(Button(100,20, lambda r=region.rid: self.interaction_system.show_region_edit_page(r), "Edit", self.fonts.small_font))
            self.component_list.append(LineDivider(config.SIDEBAR_WIDTH,2, top_padding=2))

    


    def clear_page(self):
        self.component_list = []


    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        y_offset = 10
        for component in self.component_list:
            if isinstance(component, list):
                x_offset = 0
                for subcomponent in component:
                    subcomponent.draw(screen, subcomponent.left_padding+x_offset, y_offset)
                    x_offset += subcomponent.width
                y_offset += component[0].height
            else:
                component.draw(screen, component.left_padding, y_offset)
                y_offset += component.height




