from modules.interface import Window, Color, get_foreground


def exception_handler(window: Window, e: Exception) -> None:
    window.change_section(f"{get_foreground(Color.WARNING)}\u26a0  Something went wrong!")
    window.reset()
    window.add_line(f"{get_foreground(Color.ERROR)}{type(e).__name__}: {get_foreground(Color.WARNING)}{str(e)}")
    window.add_divider()
    window.press_x_to_y("ENTER", "exit")