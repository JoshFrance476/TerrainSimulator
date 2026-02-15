import pygame
import config
from rendering.map_renderer import MapRenderer
from rendering.ui_manager import UIManager
from rendering.camera import Camera
from simulation.world import World
from simulation.map_entity import MapEntity
from utils.fps_monitor import FPSMonitor
import sys

class AppController:
    def __init__(self, screen, fonts, biome_config):
        self.biome_config = biome_config
        self.world = World(config.WORLD_ROWS, config.WORLD_COLS, self.biome_config)
        self.camera = Camera()

        self.fonts = fonts

        self.map_renderer = MapRenderer(self)
        self.ui_manager = UIManager(self, fonts, self.world, self.biome_config)

        self.fps_monitor = FPSMonitor()

        self.ui_manager.show_biome_manager_page()

        self.screen = screen

        self.player = MapEntity((50,50))

        self.selected_cell = None
        self.hovered_cell = None

        self.selected_filter = "colour"

        self.paused = True
        self.interaction_type = "view_tile"

        self.tile_paint_id = None
        self.tile_paint_enabled = False

        self.active_region_paint = None
        self.most_recent_region_paint = None

        self.focused_entity = None
        self.ui_locked = False

    
    def tick(self, events):
        self.handle_continuous_inputs()

        for event in events:
            self.handle_event(event)

        self.map_renderer.render_view(self.screen)
        self.ui_manager.render_ui(self.screen)

        self.fps_monitor.tick()
        self.ui_manager.draw_fps_counter(self.screen, self.fps_monitor.get_fps())
       
        

    def handle_continuous_inputs(self):
        if not self.focused_entity:
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
            pygame.quit()
            sys.exit()
        

        location = self.get_cell_at_mouse_position()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_component = self.ui_manager.get_clicked_component(event.pos)

                if self.ui_locked:
                    if clicked_component == self.focused_entity:
                        clicked_component.is_clicked(event)
                        self.ui_locked = False
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
                        self.focused_entity = clicked_component
                elif self.ui_manager.mouse_on_map():
                    self.mouse_down(location)
        

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                if self.focused_entity and hasattr(self.focused_entity, "stop_drag"):
                    self.focused_entity.stop_drag()
                self.mouse_up()
        
        
        if event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                if self.focused_entity:
                    if hasattr(self.focused_entity, "is_dragged"):
                        self.focused_entity.is_dragged(event)
        
        if event.type == pygame.MOUSEWHEEL:
            if self.focused_entity:
                if hasattr(self.focused_entity, "scroll"):
                    self.focused_entity.scroll(event.y)
        
        if event.type == pygame.KEYDOWN:
            if self.focused_entity:
                if hasattr(self.focused_entity, "handle_event"):
                    self.focused_entity.handle_event(event)
                if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and hasattr(self.focused_entity, "increment"):
                    self.focused_entity.increment()
                if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and hasattr(self.focused_entity, "decrement"):
                    self.focused_entity.decrement()
            else:
                if event.key == pygame.K_SPACE:
                    self.toggle_pause()
                if event.key == pygame.K_m:
                    self.toggle_move()
                if event.key == pygame.K_n:
                    self.toggle_region_place()
                if event.key == pygame.K_b:
                    self.toggle_view_tile()
                if event.key == pygame.K_z:
                    print("Debug Trigger")

    
    def clear_focus(self):
        if self.focused_entity:
            self.focused_entity.focused = False
            self.focused_entity = None

    def get_cell_at_mouse_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
            
        # Convert screen coordinates to world coordinates
        world_x = (mouse_x - config.SIDEBAR_WIDTH) + (self.camera.x_pos * config.CELL_SIZE)
        world_y = mouse_y + (self.camera.y_pos * config.CELL_SIZE)

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        return (cell_y, cell_x)

    def refresh_map_render(self):
        self.map_renderer.refresh_view()

    def select_textbox(self, textbox):
        self.selected_textbox = textbox
    
    def toggle_pause(self):
        self.paused = not self.paused
    
    def toggle_move(self):
        self.interaction_type = "move_player"
    
    def toggle_region_place(self):
        self.interaction_type = "paint_region"
    
    def toggle_tile_paint(self, tid):
        if self.interaction_type == "paint_tile":
            self.tile_paint_id = None
            self.interaction_type = "view_tile"
        else:
            self.ui_locked = True
            self.interaction_type = "paint_tile"
            self.tile_paint_id = tid
    
    def toggle_view_tile(self):
        self.interaction_type = "view_tile"
    
    def interact_with_tile(self, location):
        if self.interaction_type == "move_player":
            self.move_player_to_cell(location)
        elif self.interaction_type == "view_tile":
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
        self.world.data.set_map_data_at("biome", location, tid)
        self.process_updated_map()
    
    def paint_region(self, location, rid):
        self.world.region_manager.add_region_to_location(location, rid)
        self.refresh_map_render()
    
    def mouse_down(self, location):
        if self.interaction_type == "paint_region":
            self.create_new_region(location)
        elif self.interaction_type == "paint_tile":
            self.tile_paint_enabled = True
            self.paint_tile(location, self.tile_paint_id)
        else:
            self.interact_with_tile(location)

    def mouse_up(self):
        if self.interaction_type == "paint_region":
            self.interaction_type = "view_tile"
            self.ui_manager.show_region_setup_page()
            self.most_recent_region_paint = self.active_region_paint
            self.active_region_paint = None
        elif self.interaction_type == "paint_tile" and self.tile_paint_enabled:
            self.tile_paint_enabled = False
    
    def show_tile_manager_page(self, biome_info = {}, index = -1):
        self.ui_manager.show_tile_manager_page(biome_info, index)
    
    def create_new_region(self, location):
        region_id = self.world.region_manager.create_region(location)
        self.active_region_paint = region_id
        self.refresh_map_render()
    
    def set_painted_region_info(self, title, visible_desc, hidden_desc):
        if self.most_recent_region_paint != None:
            region = self.world.region_manager.region_list[self.most_recent_region_paint]
            region.title = title
            region.visible_desc = visible_desc
            region.hidden_desc = hidden_desc

            self.ui_manager.clear_left_page()

    def next_turn(self):
        self.camera.set_location(self.player.get_location())
        self.camera.clamp_pan()
        self.refresh_map_render()

    
    def select_cell(self, location):
        self.selected_cell = location
    
    def hover_cell(self, location):
        self.hovered_cell = location
    
    def move_player_to_cell(self, location):
        self.player.set_location(location)
        self.select_cell(location)
        self.next_turn()
    
    def set_selected_filter(self, filter_name):
        self.selected_filter = filter_name

    def get_selected_cell(self):
        return self.selected_cell
    
    def pan_camera(self, dx, dy):
        if self.interaction_type != "move_player":
            self.camera.pan(dx, dy)
            self.camera.clamp_pan()
            self.refresh_map_render()
    
    def get_camera_position(self):
        return self.camera.x_pos, self.camera.y_pos

    def get_camera_boundaries(self):
        return self.camera.x_pos, self.camera.y_pos, config.CAMERA_COLS+self.camera.x_pos, config.CAMERA_ROWS+self.camera.y_pos

    
    def get_world_data(self):
        return self.world.get_world_data()
    
    def matches_hovered_tile(self, location):
        return self.hovered_cell == location

    def new_hovered_tile(self, location):
        if self.tile_out_of_bounds(location):
            return
        if self.active_region_paint != None:
            self.paint_region(location, self.active_region_paint)        
        
        if self.tile_paint_id is not None and self.tile_paint_enabled:
            self.paint_tile(location, self.tile_paint_id)
        
        self.hover_cell(location)

        self.ui_manager.render_tooltip(location)
    
    def tile_out_of_bounds(self, location):
        return location[0] >= config.WORLD_ROWS or location[1] >= config.WORLD_COLS
    
