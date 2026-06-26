from enum import Enum, auto

class AppState:
    def __init__(self):
        self.lctrl_down = False

class PaintMode(Enum):
    BRUSH = auto()
    FILL = auto()  