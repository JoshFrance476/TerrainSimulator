import pygame
import config
import sys
from app.commands import MouseDown, MouseMove, MouseUp, MouseWheel, KeyDown, KeyUp
from app.app_state import InteractionType, LeftPage, RightPage, PaintMode

class InteractionSystem:
    def __init__(self, state, camera, player, world_editor, story_engine, world, brush, refresh_render_function, mouse_on_map_function):
        self.state = state
        self.camera = camera
        self.player = player
        self.world_editor = world_editor
        self.world = world
        self.brush = brush
        self.story_engine = story_engine
        self.refresh_render = refresh_render_function
        self.mouse_on_map = mouse_on_map_function

        self.init_start()

    def handle_continuous(self, keys, mouse_pos):
        if not self.state.focused_entity and self.state.interaction_type is not InteractionType.MOVE_PLAYER:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self._pan(-config.PAN_STEP, 0)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self._pan(config.PAN_STEP, 0)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self._pan(0, -config.PAN_STEP)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self._pan(0, config.PAN_STEP)

        self.tile_interaction(self.get_cell_at_mouse_position(mouse_pos))

    def handle(self, cmd):
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
        elif isinstance(cmd, KeyUp):
            self._key_up(cmd)
        elif cmd.type == pygame.QUIT:
            self._quit()
    
    def init_start(self):
        self.player.set_location(self.world.biome_config.get_starting_location())
        self.select_cell(self.player.location)
        self.camera.set_location(self.player.get_location())
        self.camera.clamp_pan()
        self.refresh_render()
 
    def set_region_info(self, title, visible_desc, hidden_desc, region_id):
        self.world_editor.set_painted_region_info(title, visible_desc, hidden_desc, region_id)
        self.state.active_region_edit_id = None
        self.state.interaction_type = InteractionType.VIEW_TILE

        self.state.left_page = LeftPage.BIOME_EDITOR
    
    def submit_pending_interaction_action(self, action_index):
        self.story_engine.choose_action(action_index, self.state.selected_cell)
        self.refresh_render()
        self.state.update_right_page = True
    
    def submit_custom_pending_interaction_action(self, action_desc):
        self.story_engine.submit_custom_action(action_desc)
        self.state.update_right_page = True
    
    def exit_scenario(self):
        self.story_engine.clear_scenario()
        self.state.update_right_page = True
    
    def prompt_scenario(self):
        self.story_engine.generate_scene_interaction(self.state.selected_cell)
        self.state.update_right_page = True
    
    
    def generate_map(self):
        self.world.generate_map()
        self.refresh_render()

    def set_hovered_cell(self, location):
        self.state.hovered_cell = location
    
    def select_cell(self, location):
        self.state.selected_cell = location
        self.state.left_page = LeftPage.VIEW_LOCATION

    def show_region_edit_page(self, region_id):
        self.state.interaction_type = InteractionType.PAINT_REGION
        self.state.active_region_edit_id = region_id

        self.state.left_page = LeftPage.REGION_EDITOR
    
    def add_biome(self, name, h, s, v, traversal_cost, description):
        self.world_editor.add_biome(name, h, s, v, traversal_cost, description)
        self.state.left_page = LeftPage.BIOME_EDITOR
        self.refresh_render()
    
    def edit_biome(self, index, name, h, s, v, traversal_cost, description):
        self.world_editor.edit_biome(index, name, h, s, v, traversal_cost, description)
        self.state.left_page = LeftPage.BIOME_EDITOR
        self.refresh_render()
    
    def clear_focus(self):
        if self.state.focused_entity:
            self.state.focused_entity.focused = False
            self.state.focused_entity = None
    
    def toggle_move(self):
        self.state.interaction_type = InteractionType.MOVE_PLAYER
    
    def toggle_region_place(self):
        self.state.interaction_type = InteractionType.PAINT_REGION
    
    def toggle_tile_paint(self, tid):
        if self.state.interaction_type == InteractionType.PAINT_TILE:
            self.state.active_biome_edit_id = None
            self.state.interaction_type = InteractionType.VIEW_TILE
        else:
            self.state.interaction_type = InteractionType.PAINT_TILE
            self.state.active_biome_edit_id = tid
    
    def toggle_view_tile(self):
        self.state.interaction_type = InteractionType.VIEW_TILE
    
    def interact_with_tile(self, location):
        if self.state.interaction_type == InteractionType.VIEW_TILE:
            self.select_cell(location)
    
    def set_brush_attributes(self, size = None, strength = None):
        if size:
            self.brush.size = size
        if strength:
            self.brush.strength = strength
    
    def toggle_brush_mode(self):
        self.world_editor.paint_mode = PaintMode.BRUSH
    
    def toggle_fill_mode(self):
        self.world_editor.paint_mode = PaintMode.FILL
    
    def toggle_elevation_updates_biome(self, checkbox_value):
        self.world_editor.elevation_updates_biome = checkbox_value

    def tile_interaction(self, location):
        if not self.mouse_on_map():
            return
        
        # Interactions to perform continuously on the same tile
        if self.state.interaction_type is InteractionType.EDIT_ELEVATION:
            if self.state.left_mouse_down:
                self.world_editor.edit_elevation(location)
                self.refresh_render()
            elif self.state.right_mouse_down:
                self.world_editor.edit_elevation(location, negative=True)
                self.refresh_render()
        
        # Interactions to only perform once on each tile
        if not self._matches_hovered_tile(location):
            if self.state.left_mouse_down and self.state.interaction_type is InteractionType.PAINT_REGION:
                self.world_editor.paint_region(location, self.state.active_region_edit_id)
                self.refresh_render()      
            elif self.state.right_mouse_down and self.state.interaction_type is InteractionType.PAINT_REGION:
                self.world_editor.remove_region(location, self.state.active_region_edit_id)
                self.refresh_render()
            
            if self.state.left_mouse_down and self.state.interaction_type is InteractionType.PAINT_TILE:
                self.world_editor.paint_biome(location, self.state.active_biome_edit_id)
                self.refresh_render()
        
        self.set_hovered_cell(location)
    
    def _mouse_down(self, cmd: MouseDown):
        if cmd.button == 3:
            self.state.right_mouse_down = True
            return
        elif cmd.button != 1:
            return
    
        self.state.left_mouse_down = True

        self.clear_focus()

        if self.mouse_on_map():
            self._map_mouse_down(self.get_cell_at_mouse_position(cmd.pos))
        elif cmd.clicked_ui:
            if hasattr(cmd.clicked_ui, "is_clicked"):
                cmd.clicked_ui.is_clicked(cmd)
            if hasattr(cmd.clicked_ui, "focused"):
                cmd.clicked_ui.focused = True
                self.state.focused_entity = cmd.clicked_ui
                
    def _map_mouse_down(self, location):
        mode = self.state.interaction_type
        if mode == InteractionType.PAINT_REGION:
            if self.state.active_region_edit_id is None:
                self.state.active_region_edit_id = self._create_new_region()
            self.world_editor.paint_region(location, self.state.active_region_edit_id)
            self.refresh_render()

        elif mode == InteractionType.PAINT_TILE:
            self.world_editor.paint_biome(location, self.state.active_biome_edit_id)
            self.refresh_render()

        elif mode == InteractionType.EDIT_ELEVATION:
            self.world_editor.edit_elevation(location)
            self.refresh_render()

        else:
            self.interact_with_tile(location)

    def _mouse_up(self, cmd: MouseUp):
        if cmd.button == 3:
            self.state.right_mouse_down = False
            return
        elif cmd.button != 1:
            return

        self.state.left_mouse_down = False

        if self.state.focused_entity and hasattr(self.state.focused_entity, "stop_drag"):
            self.state.focused_entity.stop_drag()

        if self.state.interaction_type is InteractionType.PAINT_REGION:
            if self.state.active_region_edit_id is not None:
                self.state.left_page = LeftPage.REGION_EDITOR

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
            self.state.interaction_type = InteractionType.MOVE_PLAYER
        elif cmd.key == pygame.K_n:
            self.state.interaction_type = InteractionType.PAINT_REGION
        elif cmd.key == pygame.K_b:
            self.state.interaction_type = InteractionType.VIEW_TILE
        elif cmd.key == pygame.K_v:
            self.state.interaction_type = InteractionType.EDIT_ELEVATION
        elif cmd.key == pygame.K_q:
            self.state.debug_mode = not self.state.debug_mode
            self.refresh_render()
        elif cmd.key == pygame.K_LCTRL:
            self.state.lctrl_down = True
        
        if self.state.interaction_type == InteractionType.MOVE_PLAYER:
            if cmd.key in (pygame.K_w, pygame.K_UP):
                self.player.move_north()
                direction = "north"
            elif cmd.key in (pygame.K_d, pygame.K_RIGHT):
                self.player.move_east()
                direction = "east"
            elif cmd.key in (pygame.K_s, pygame.K_DOWN):
                self.player.move_south()
                direction = "south"
            elif cmd.key in (pygame.K_a, pygame.K_LEFT):
                self.player.move_west()
                direction = "west"
            else:
                return
            
            self.select_cell(self.player.location)
            self.camera.set_location(self.player.get_location())
            self.camera.clamp_pan()
            self.story_engine.add_to_movement_history({"direction": direction, "biome": self.world.get_biome_data_at_location(self.player.location)["name"]})
            self.refresh_render()

    def _key_up(self, cmd: KeyUp):
        if cmd.key == pygame.K_LCTRL:
            self.state.lctrl_down = False
    
    def _quit(self):
        print(self.story_engine.get_token_usage())
        pygame.quit()
        sys.exit()

    def _pan(self, dx, dy):
        if self.state.interaction_type is not InteractionType.MOVE_PLAYER:
            self.camera.pan(dx, dy)
            self.refresh_render()

    def _create_new_region(self):
        return self.world_editor.create_region()

    def _matches_hovered_tile(self, location):
        return self.state.hovered_cell == location

    def get_cell_at_mouse_position(self, mouse_pos):
        # Convert screen coordinates to world coordinates
        world_x = (mouse_pos[0] - config.SIDEBAR_WIDTH) + (self.camera.x_pos * config.CELL_SIZE)
        world_y = mouse_pos[1] + (self.camera.y_pos * config.CELL_SIZE)

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        return (cell_y, cell_x)