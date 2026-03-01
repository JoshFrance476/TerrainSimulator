import pygame
import config
from utils.commands import MouseDown, MouseMove, MouseUp, MouseWheel, KeyDown

class InteractionSystem:
    def __init__(self, state, camera, player, world_editor, storyteller, world, refresh_render_function, get_cell_at_mouse_position_function, mouse_on_map_function):
        self.state = state
        self.camera = camera
        self.player = player
        self.world_editor = world_editor
        self.world = world
        self.storyteller = storyteller
        self.refresh_render = refresh_render_function
        self.get_cell = get_cell_at_mouse_position_function
        self.mouse_on_map = mouse_on_map_function

    def handle_continuous(self, keys):
        if not self.state.focused_entity:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self._pan(-config.PAN_STEP, 0)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self._pan(config.PAN_STEP, 0)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self._pan(0, -config.PAN_STEP)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self._pan(0, config.PAN_STEP)
        
        location = self.get_cell()

        if not self._matches_hovered_tile(location):
            self.new_hovered_tile(location)


    def handle(self, cmd):
        # Implement: quit, mousedown, mouseup, motion drag, wheel scroll, keydown mapping
        if isinstance(cmd, MouseDown):
            self._mouse_down(cmd)
        elif isinstance(cmd, MouseUp):
            self._mouse_up(cmd)
        elif isinstance(cmd, MouseMove):
            self._mouse_move(cmd)
        elif isinstance(cmd, MouseWheel):
            self._mouse_wheel(cmd)
        elif isinstance(cmd, KeyDown):
            self._key_down(cmd)


    def new_hovered_tile(self, location):
        if self.tile_out_of_bounds(location):
            return
        if self.state.left_mouse_down and self.state.active_region_paint is not None:
            self.world_editor.paint_region(location, self.state.active_region_paint)
            self.refresh_render()      
        elif self.state.right_mouse_down and self.state.most_recent_region_paint is not None:
            self.world_editor.remove_region(location, self.state.most_recent_region_paint)
            self.refresh_render()
        elif self.state.left_mouse_down and self.state.interaction_type == "edit_elevation":
            self.world_editor.edit_elevation(location)
            self.refresh_render()
        elif self.state.right_mouse_down and self.state.interaction_type == "edit_elevation":
            self.world_editor.edit_elevation(location, negative=True)
            self.refresh_render()
        
        if self.state.tile_paint_id is not None and self.state.tile_paint_enabled:
            self.world_editor.paint_tile(location, self.state.tile_paint_id)
            self.refresh_render()
        
        self.hover_cell(location)
    
    def set_region_info(self, title, visible_desc, hidden_desc, region_id):
        self.world_editor.set_painted_region_info(title, visible_desc, hidden_desc, region_id)
        self.state.most_recent_region_paint = None
        self.state.interaction_type = "view_tile"

        self.state.left_page = "biome_editor"
    
    def move_player_to_cell(self, location):
        self.player.set_location(location)
        self.select_cell(location)
        self.camera.set_location(self.player.get_location())
        self.camera.clamp_pan()
        self.refresh_render()
    
    def submit_pending_interaction_action(self, action_index):
        self.storyteller.submit_action(action_index)
        self.state.right_page = "scenario"
    
    def exit_scenario(self):
        self.storyteller.current_scenario = None
        self.state.right_page = "scenario"
    
    def prompt_scenario(self):
        self.storyteller.prompt_new_interaction()
        self.state.right_page = "scenario"
    
    def save_map(self, file_name):
        self.world.save_map("saved_maps/"+file_name)
    
    def load_map(self, file_name):
        self.world.load_map("saved_maps/"+file_name+".npz")
        self.refresh_render()
    
    def hover_cell(self, location):
        self.state.hovered_cell = location
    
    def select_cell(self, location):
        self.state.selected_cell = location
        self.state.left_page = "location"


    def show_region_edit_page(self, region_id):
        self.state.interaction_type = "paint_region"
        self.state.most_recent_region_paint = region_id

        self.state.left_page = "region_editor"
    
    def add_biome(self, name, h, s, v, traversal_cost):
        self.world_editor.add_biome(name, h, s, v, traversal_cost)
        self.state.left_page = "biome_editor"
        self.refresh_render()
    
    def edit_biome(self, index, name, h, s, v, traversal_cost):
        self.world_editor.edit_biome(index, name, h, s, v, traversal_cost)
        self.state.left_page = "biome_editor"
        self.refresh_render()
    
    
    def clear_focus(self):
        if self.state.focused_entity:
            self.state.focused_entity.focused = False
            self.state.focused_entity = None
    
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
    
    def tile_out_of_bounds(self, location):
        return location[0] >= config.WORLD_ROWS or location[1] >= config.WORLD_COLS

    def _mouse_down(self, cmd: MouseDown):
        if cmd.button == 3:
            self.state.right_mouse_down = True
            return
        elif cmd.button != 1:
            return
    
        self.state.left_mouse_down = True

        if self.state.ui_locked:
            if cmd.clicked_ui == self.state.focused_entity:
                cmd.clicked_ui.is_clicked(cmd)  # careful: you may keep event instead
                self.state.ui_locked = False
                self.clear_focus()
            else:
                if self.mouse_on_map():
                    self._map_mouse_down(cmd.location)
            return

        self.clear_focus()

        if cmd.clicked_ui:
            if hasattr(cmd.clicked_ui, "is_clicked"):
                cmd.clicked_ui.is_clicked(cmd)  # or store pygame event in command
            if hasattr(cmd.clicked_ui, "focused"):
                cmd.clicked_ui.focused = True
                self.state.focused_entity = cmd.clicked_ui
        elif self.mouse_on_map():
            self._map_mouse_down(cmd.location)

    def _map_mouse_down(self, location):
        mode = self.state.interaction_type
        if mode == "paint_region":
            if self.state.active_region_paint is None:
                if self.state.most_recent_region_paint is not None:
                    self.state.active_region_paint = self.state.most_recent_region_paint
                else:
                    self.state.active_region_paint = self._create_new_region()
            self.world_editor.paint_region(location, self.state.active_region_paint)
            self.refresh_render()

        elif mode == "paint_tile":
            self.state.tile_paint_enabled = True
            self.world_editor.paint_tile(location, self.state.tile_paint_id)
            self.refresh_render()

        elif mode == "edit_elevation":
            self.world_editor.edit_elevation(location, self.world_editor.brush.brush_strength)
            self.refresh_render()

        else:
            self._interact_with_tile(location)

    def _mouse_up(self, cmd: MouseUp):
        if cmd.button == 3:
            self.state.right_mouse_down = False
            return
        elif cmd.button != 1:
            return

        self.state.left_mouse_down = False

        if self.state.focused_entity and hasattr(self.state.focused_entity, "stop_drag"):
            self.state.focused_entity.stop_drag()

        if self.state.interaction_type == "paint_region":
            if self.state.active_region_paint is not None:
                self.state.active_region_edit_id = self.state.active_region_paint
                self.state.left_page = "region_editor"
                self.state.most_recent_region_paint = self.state.active_region_paint
            self.state.active_region_paint = None

        elif self.state.interaction_type == "paint_tile" and self.state.tile_paint_enabled:
            self.state.tile_paint_enabled = False

    def _mouse_move(self, cmd: MouseMove):
        if cmd.left_down and self.state.focused_entity and hasattr(self.state.focused_entity, "is_dragged"):
            self.state.focused_entity.is_dragged(cmd)

    def _mouse_wheel(self, cmd: MouseWheel):
        if self.state.focused_entity and hasattr(self.state.focused_entity, "scroll"):
            self.state.focused_entity.scroll(cmd.y)

    def _key_down(self, cmd: KeyDown):
        # Port keybindings from AppController
        if self.state.focused_entity:
            ent = self.state.focused_entity
            if hasattr(ent, "handle_event"):
                ent.handle_event(cmd)
            if (cmd.key in (pygame.K_d, pygame.K_RIGHT)) and hasattr(ent, "increment"):
                ent.increment()
            if (cmd.key in (pygame.K_a, pygame.K_LEFT)) and hasattr(ent, "decrement"):
                ent.decrement()
            return

        if cmd.key == pygame.K_SPACE:
            self.state.paused = not self.state.paused
        elif cmd.key == pygame.K_m:
            self.state.interaction_type = "move_player"
        elif cmd.key == pygame.K_n:
            self.state.interaction_type = "paint_region"
        elif cmd.key == pygame.K_b:
            self.state.interaction_type = "view_tile"
        elif cmd.key == pygame.K_v:
            self.state.interaction_type = "edit_elevation"
        # etc

    def _interact_with_tile(self, location):
        if self.state.interaction_type == "move_player":
            self.move_player(location)
        elif self.state.interaction_type == "view_tile":
            self.select_cell(location)

    def _pan(self, dx, dy):
        if self.state.interaction_type != "move_player":
            self.camera.pan(dx, dy)
            self.camera.clamp_pan()
            self.refresh_render()

    def _create_new_region(self):
        return self.world_editor.create_region()

    def _matches_hovered_tile(self, location):
        return self.state.hovered_cell == location