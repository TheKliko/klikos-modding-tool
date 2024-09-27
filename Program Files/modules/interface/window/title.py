from os import system


def set(title: str = "py.exe") -> None:
    system(f'title {title}')