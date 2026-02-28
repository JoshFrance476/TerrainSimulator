import pygame
import config
from app_state import AppState
from rendering.map_renderer import MapRenderer
from rendering.ui_manager import UIManager
from rendering.camera import Camera
from simulation.world import World
from simulation.map_entity import MapEntity
from utils.fps_monitor import FPSMonitor
from storyteller.storyteller_manager import StorytellerManager
from brush_manager import BrushManager
import sys

class AppController:
    def __init__(self, screen, fonts, biome_config):
        self.biome_config = biome_config
        self.world = World(config.WORLD_ROWS, config.WORLD_COLS, self.biome_config)
        self.camera = Camera()

        self.state = AppState()
        
        self.player = MapEntity((self.biome_config.get_starting_location()))
        self.camera.set_location(self.player.get_location())

        self.fonts = fonts

        self.map_renderer = MapRenderer(self)
        self.ui_manager = UIManager(self, fonts, self.world, self.biome_config)

        self.fps_monitor = FPSMonitor()

        self.storyteller = StorytellerManager(self)

        self.brush_manager = BrushManager()

        self.screen = screen


        self.ui_manager.show_biome_manager_page()
        self.ui_manager.show_current_scenario_screen()

    
    def tick(self, events):
        self.handle_continuous_inputs()

        for event in events:
            self.handle_event(event)

        self.map_renderer.render_view(self.screen)

        self.fps_monitor.tick()

        self.ui_manager.draw_fps_counter(self.screen, self.fps_monitor.get_fps())
        self.ui_manager.render_ui(self.screen)

       
        

    def handle_continuous_inputs(self):
        if not self.state.focused_entity:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.pan_camera(-config.PAN_STEP, 0)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.pan_camera(config.PAN_STEP, 0)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.pan_camera(0, -config.PAN_STEP)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.pan_camera(0, config.PAN_STEP)

        location = self.get_cell_at_mouse_position()

        if not self.matches_hovered_tile(location):
            self.new_hovered_tile(location)
    

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            print(f"Total input tokens: {self.storyteller.input_token_count}\nTotal output tokens: {self.storyteller.output_token_count}")
            print(f"Total cost (gpt-oss-120b): {round(self.storyteller.input_token_count*0.000015+self.storyteller.output_token_count*0.00006, 5)} cents")
            pygame.quit()
            sys.exit()
        

        location = self.get_cell_at_mouse_position()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_component = self.ui_manager.get_clicked_component(event.pos)

                if self.state.ui_locked:
                    if clicked_component == self.state.focused_entity:
                        clicked_component.is_clicked(event)
                        self.state.ui_locked = False
                        self.clear_focus()
                    else:
                        if self.ui_manager.mouse_on_map():
                            self.mouse_down(location)
                    return

                self.clear_focus()

                if clicked_component:
                    if hasattr(clicked_component, "is_clicked"):
                        clicked_component.is_clicked(event)
                    if hasattr(clicked_component, "focused"):
                        clicked_component.focused = True
                        self.state.focused_entity = clicked_component
                elif self.ui_manager.mouse_on_map():
                    self.mouse_down(location)
        

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                if self.state.focused_entity and hasattr(self.state.focused_entity, "stop_drag"):
                    self.state.focused_entity.stop_drag()
                self.mouse_up()
        
        
        if event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                if self.state.focused_entity:
                    if hasattr(self.state.focused_entity, "is_dragged"):
                        self.state.focused_entity.is_dragged(event)
        
        if event.type == pygame.MOUSEWHEEL:
            if self.state.focused_entity:
                if hasattr(self.state.focused_entity, "scroll"):
                    self.state.focused_entity.scroll(event.y)
        
        if event.type == pygame.KEYDOWN:
            if self.state.focused_entity:
                if hasattr(self.state.focused_entity, "handle_event"):
                    self.state.focused_entity.handle_event(event)
                if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and hasattr(self.state.focused_entity, "increment"):
                    self.state.focused_entity.increment()
                if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and hasattr(self.state.focused_entity, "decrement"):
                    self.state.focused_entity.decrement()
            else:
                if event.key == pygame.K_SPACE:
                    self.toggle_pause()
                if event.key == pygame.K_m:
                    self.toggle_move()
                if event.key == pygame.K_n:
                    self.toggle_region_place()
                if event.key == pygame.K_b:
                    self.toggle_view_tile()
                if event.key == pygame.K_v:
                    self.toggle_edit_elevation()
                if event.key == pygame.K_z:
                    self.load_map("demo")

    
    def clear_focus(self):
        if self.state.focused_entity:
            self.state.focused_entity.focused = False
            self.state.focused_entity = None
    
    def get_regions_at_location(self, location):
        return self.world.get_regions_at_location(location)
        
    def show_menu(self):
        self.ui_manager.show_menu = True
    
    def hide_menu(self):
        self.ui_manager.show_menu = False

    def get_cell_at_mouse_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
            
        # Convert screen coordinates to world coordinates
        world_x = (mouse_x - config.SIDEBAR_WIDTH) + (self.camera.x_pos * config.CELL_SIZE)
        world_y = mouse_y + (self.camera.y_pos * config.CELL_SIZE)

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        return (cell_y, cell_x)
    
    def get_character_notebook(self):
        return self.storyteller.get_notebook()
    
    def get_character_history(self):
        return self.storyteller.get_character_history()

    def refresh_map_render(self):
        self.map_renderer.refresh_view()
    
    def prompt_scenario(self):
        self.storyteller.prompt_new_interaction()
        self.ui_manager.show_current_scenario_screen()
    
    def submit_pending_interaction_action(self, action_index):
        self.storyteller.submit_action(action_index)
        self.ui_manager.show_current_scenario_screen()
    
    def get_current_scenario(self):
        return self.storyteller.current_scenario
    
    def exit_scenario(self):
        self.storyteller.current_scenario = None
        self.ui_manager.show_current_scenario_screen()
    
    def toggle_move(self):
        self.state.interaction_type = "move_player"
    
    def toggle_region_place(self):
        self.state.interaction_type = "paint_region"
    
    def toggle_tile_paint(self, tid):
        if self.state.interaction_type == "paint_tile":
            self.state.tile_paint_id = None
            self.state.interaction_type = "view_tile"
        else:
            self.state.ui_locked = True
            self.state.interaction_type = "paint_tile"
            self.state.tile_paint_id = tid
    
    def toggle_view_tile(self):
        self.state.interaction_type = "view_tile"
    
    def interact_with_tile(self, location):
        if self.state.interaction_type == "move_player":
            self.move_player_to_cell(location)
        elif self.state.interaction_type == "view_tile":
            self.select_cell(location)
    
    def add_biome(self, name, h, s, v, traversal_cost):
        self.biome_config.add_biome(name, h, s, v, traversal_cost)
        self.ui_manager.show_biome_manager_page()
        self.process_updated_map()
    
    def edit_biome(self, index, name, h, s, v, traversal_cost):
        self.biome_config.edit_biome(index, name, h, s, v, traversal_cost)
        self.ui_manager.show_biome_manager_page()
        self.process_updated_map()
    
    def process_updated_map(self):
        self.world.data.update_stage_3()
        self.refresh_map_render()
    
    def paint_tile(self, location, tid):
        for brush_location in self.brush_manager.get_brush(location):
            self.world.data.set_map_data_at("biome", brush_location, tid)
        self.process_updated_map()
    
    def paint_edit_elevation(self, location, strength):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL]:
            self.world.apply_smoothing_elevation_mask(self.brush_manager.get_brush_mask(location, strength, True))
        else:
            self.world.apply_edit_elevation_mask(self.brush_manager.get_brush_mask(location, strength))
        self.world.update_steepness()
        self.world.update_biome()
        self.world.update_stage_3()
        self.refresh_map_render()
    
    def toggle_edit_elevation(self):
        self.state.interaction_type = "edit_elevation"

    def paint_region(self, location, rid):
        for brush_location in self.brush_manager.get_brush(location):
            self.world.region_manager.add_region_to_location(brush_location, rid)
        self.refresh_map_render()
    
    def remove_region(self, location, rid):
        for brush_location in self.brush_manager.get_brush(location):
            self.world.region_manager.remove_region_from_location(brush_location, rid)
        self.refresh_map_render()
    
    
    def mouse_down(self, location):
        if self.state.interaction_type == "paint_region":
            if self.state.active_region_paint is None:
                if self.state.most_recent_region_paint is not None:
                    self.state.active_region_paint = self.state.most_recent_region_paint
                else:
                    self.state.active_region_paint = self.create_new_region()
            self.paint_region(location, self.state.active_region_paint)
        elif self.state.interaction_type == "paint_tile":
            self.state.tile_paint_enabled = True
            self.paint_tile(location, self.state.tile_paint_id)
        elif self.state.interaction_type == "edit_elevation":
            self.paint_edit_elevation(location, self.brush_manager.brush_strength)
        else:
            self.interact_with_tile(location)

    def mouse_up(self):
        if self.state.interaction_type == "paint_region":

            if self.state.active_region_paint is not None:
                self.ui_manager.show_region_setup_page(self.state.active_region_paint)
                self.state.most_recent_region_paint = self.state.active_region_paint

            self.state.active_region_paint = None
        elif self.state.interaction_type == "paint_tile" and self.state.tile_paint_enabled:
            self.state.tile_paint_enabled = False
    
    def get_region(self, region_id):
        return self.world.get_region(region_id)
    
    def show_tile_manager_page(self, biome_info = {}, index = -1):
        self.ui_manager.show_tile_manager_page(biome_info, index)
    
    def create_new_region(self):
        region_id = self.world.region_manager.create_region()
        return region_id
    
    def set_painted_region_info(self, title, visible_desc, hidden_desc, region_id = None):
        if region_id is not None:
            region = self.world.region_manager.region_list[region_id]
        elif self.state.most_recent_region_paint != None:
            region = self.world.region_manager.region_list[self.state.most_recent_region_paint]
        region.title = title
        region.visible_desc = visible_desc
        region.hidden_desc = hidden_desc

        self.state.most_recent_region_paint = None
        self.state.interaction_type = "view_tile"

        self.ui_manager.show_biome_manager_page()
    
    def show_region_edit_page(self, region_id):
        self.ui_manager.show_region_setup_page(region_id)
        self.state.interaction_type = "paint_region"
        self.state.most_recent_region_paint = region_id

    def next_turn(self):
        self.camera.set_location(self.player.get_location())
        self.camera.clamp_pan()
        self.refresh_map_render()

    
    def select_cell(self, location):
        self.state.selected_cell = location
        self.ui_manager.show_location_info_page()
    
    def hover_cell(self, location):
        self.state.hovered_cell = location
    
    def move_player_to_cell(self, location):
        self.player.set_location(location)
        self.select_cell(location)
        self.next_turn()
    
    def set_selected_filter(self, filter_name):
        self.state.selected_filter = filter_name

    def get_selected_cell(self):
        return self.state.selected_cell

    def get_hovered_cell(self):
        return self.state.hovered_cell

    
    def pan_camera(self, dx, dy):
        if self.state.interaction_type != "move_player":
            self.camera.pan(dx, dy)
            self.camera.clamp_pan()
            self.refresh_map_render()
    
    def get_camera_position(self):
        return self.camera.x_pos, self.camera.y_pos

    def get_camera_boundaries(self):
        return self.camera.x_pos, self.camera.y_pos, config.CAMERA_COLS+self.camera.x_pos, config.CAMERA_ROWS+self.camera.y_pos

    
    def get_world_data(self):
        return self.world.get_world_data()

    def get_biome_at(self, location):
        return self.world.get_biome_at(location)

    def get_semantic_tile_data(self, location):
        return self.world.get_semantic_tile_data(location)
    
    def matches_hovered_tile(self, location):
        return self.state.hovered_cell == location

    def new_hovered_tile(self, location):
        if self.tile_out_of_bounds(location):
            return
        if pygame.mouse.get_pressed()[0] and self.state.active_region_paint is not None:
            self.paint_region(location, self.state.active_region_paint)        
        elif pygame.mouse.get_pressed()[2] and self.state.most_recent_region_paint is not None:
            self.remove_region(location, self.state.most_recent_region_paint)
        elif pygame.mouse.get_pressed()[0] and self.state.interaction_type == "edit_elevation":
            self.paint_edit_elevation(location, self.brush_manager.brush_strength)
        elif pygame.mouse.get_pressed()[2] and self.state.interaction_type == "edit_elevation":
            self.paint_edit_elevation(location, -self.brush_manager.brush_strength)
        
        if self.state.tile_paint_id is not None and self.state.tile_paint_enabled:
            self.paint_tile(location, self.state.tile_paint_id)
        
        self.hover_cell(location)

        self.ui_manager.render_tooltip(location)
    
    def tile_out_of_bounds(self, location):
        return location[0] >= config.WORLD_ROWS or location[1] >= config.WORLD_COLS
    
    def save_map(self, file_name):
        self.world.save_map("saved_maps/"+file_name)
    
    def load_map(self, file_name):
        self.world.load_map("saved_maps/"+file_name+".npz")
        self.refresh_map_render()
    
    
