import os


def full() -> os.terminal_size:
    return os.get_terminal_size()


def width() -> int:
    return full().columns


def height() -> int:
    return full().lines