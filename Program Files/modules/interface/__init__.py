from .color import *
from .clear import clear
from .print import _print as print
from .alignment import Alignment
from .window import Window


def set_color(color: str) -> str:
    if color is None:
        return ''
    elif color == Color.RESET:
        return color
    
    return get_foreground(color)