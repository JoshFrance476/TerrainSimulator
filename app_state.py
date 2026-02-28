class AppState:
    def __init__(self):
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

        self.left_page = "biome_editor"
        self.right_page = "scenario"

        self.show_menu = False

        self.active_region_edit_id = None
        self.active_biome_edit_id = None