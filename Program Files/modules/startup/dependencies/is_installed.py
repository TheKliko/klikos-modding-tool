from importlib.util import find_spec


def is_installed(library: str) -> bool:
    return find_spec(library) is not None