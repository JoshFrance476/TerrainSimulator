from dataclasses import dataclass
from typing import Tuple, Optional, Any

Location = Tuple[int, int]

@dataclass
class MouseDown:
    button: int
    pos: Tuple[int, int]
    location: Location
    clicked_ui: Optional[Any]

@dataclass
class MouseUp:
    button: int
    pos: Tuple[int, int]

@dataclass
class MouseMove:
    pos: Tuple[int, int]
    left_down: bool

@dataclass
class MouseWheel:
    y: int

@dataclass
class KeyDown:
    key: int
    unicode: int