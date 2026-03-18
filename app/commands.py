from dataclasses import dataclass
from typing import Tuple, Optional, Any

@dataclass
class MouseDown:
    button: int
    pos: Tuple[int, int]
    clicked_ui: Optional[Any]

@dataclass
class MouseUp:
    button: int

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

@dataclass
class KeyUp:
    key: int