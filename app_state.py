from enum import Enum, auto

class AppState:
    def __init__(self):
        self.selected_cell = None
        self.hovered_cell = None

        self.interaction_type = InteractionType.VIEW_TILE

        self.focused_entity = None
        self.ui_locked = False

        self.left_page = LeftPage.BIOME_EDITOR
        self.update_right_page = False

        self.show_menu = False

        self.active_region_edit_id = None
        self.active_biome_edit_id = None

        self.left_mouse_down = False
        self.right_mouse_down = False

        self.debug_mode = False


class InteractionType(Enum):
    VIEW_TILE = auto()
    MOVE_PLAYER = auto()
    PAINT_REGION = auto()
    PAINT_TILE = auto()
    EDIT_ELEVATION = auto()

class LeftPage(Enum):
    VIEW_LOCATION = auto()
    BIOME_EDITOR = auto()
    TILE_EDITOR = auto()
    REGION_EDITOR = auto()
    VIEW_CHARACTER = auto()

class RightPage(Enum):
    VIEW_SCENARIO = auto()

class PaintMode(Enum):
    BRUSH = auto()
    FILL = auto()  