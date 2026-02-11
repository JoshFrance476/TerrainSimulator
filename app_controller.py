import pygame
import config
from rendering.map_renderer import MapRenderer

class AppController:
    def __init__(self, world, camera, player, screen):
        self.world = world
        self.camera = camera
        self.map_renderer = MapRenderer(self)

        self.screen = screen

        self.player = player

        self.selected_cell = None
        self.hovered_cell = None

        self.selected_filter = "colour"

        self.paused = True
        self.interaction_type = "view_tile"

        self.selected_textbox = None
    
    def tick(self):
        self.map_renderer.render_view(self.screen)
    
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
    
    def toggle_view_tile(self):
        self.interaction_type = "view_tile"
    
    def interact_with_tile(self, r, c):
        if self.interaction_type == "move_player":
            self.move_player_to_cell(r, c)
        elif self.interaction_type == "view_tile":
            self.select_cell(r, c)
        elif self.interaction_type == "paint_region":
            self.paint_region((r,c))
    
    def paint_region(self, location):
        self.world.region_manager.create_region(location)
        self.refresh_map_render()

    def next_turn(self):
        self.camera.set_location(self.player.get_location())
        self.camera.clamp_pan()
        self.refresh_map_render()
    
    def cycle_left_sidebar(self, delta):
        self.active_left_sidebar = (self.active_left_sidebar + delta) % 4

    def cycle_right_sidebar(self, delta):
        self.active_right_sidebar = (self.active_right_sidebar + delta) % 4
    
    def select_cell(self, r, c):
        self.selected_cell = (r, c)
    
    def hover_cell(self, r, c):
        self.hovered_cell = (r, c)
    
    def move_player_to_cell(self, r, c):
        self.player.set_location((r, c))
        self.select_cell(r, c)
        self.next_turn()
    
    def set_selected_filter(self, filter_name):
        self.selected_filter = filter_name

    def get_selected_cell(self):
        return self.selected_cell
    
    def pan_camera(self, dx, dy):
        if self.interaction_type != "move_player":
            self.camera.pan(dx, dy)
            self.refresh_map_render()
    
    def get_camera_position(self):
        return self.camera.x_pos, self.camera.y_pos

    def get_camera_boundaries(self):
        return self.camera.x_pos, self.camera.y_pos, config.CAMERA_COLS+self.camera.x_pos, config.CAMERA_ROWS+self.camera.y_pos

    def get_cell_at_mouse_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
            
        # Convert screen coordinates to world coordinates
        world_x = (mouse_x - config.SIDEBAR_WIDTH) + (self.camera.x_pos * config.CELL_SIZE)
        world_y = mouse_y + (self.camera.y_pos * config.CELL_SIZE)

        # Convert world coordinates to grid cell indices
        cell_x = int(world_x // config.CELL_SIZE)
        cell_y = int(world_y // config.CELL_SIZE)

        return cell_y, cell_x
    
    def get_world_data(self):
        return self.world.get_world_data()
    
