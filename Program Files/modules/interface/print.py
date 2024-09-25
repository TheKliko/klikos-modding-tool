import os
from typing import Literal


from .color import get_foreground, Color


def _print(*values: object, sep: str = ' ', end: str = '\n', color: str = None, alignment: Literal['<','>','^'] = '<'):
    width: int = os.get_terminal_size().columns
    text: str = sep.join(str(v) for v in values)
    for line in text.split('\n'):
        string: str = f"{get_foreground(color)}{line:{alignment}{width}}{Color.RESET}{end}"
        print(string, end='')