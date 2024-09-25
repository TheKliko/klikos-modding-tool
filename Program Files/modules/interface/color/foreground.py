from .convert import hex_to_rgb


def foreground(color: str = None) -> None:
    if color == None:
        print("\033[0m")
    print(get_foreground(color))


def get_foreground(color: str = None) -> str:
    if color is None:
        return "\033[0m"

    r, g, b = hex_to_rgb(color)

    return f"\033[38;2;{r};{g};{b}m"