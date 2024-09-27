from .convert import hex_to_rgb


def background(color: str = None) -> None:
    if color is None:
        color = "#0c0c0c"

    r, g, b = hex_to_rgb(color)
    print(f"\033]11;rgb:{r:02x}/{g:02x}/{b:02x}\033\\")