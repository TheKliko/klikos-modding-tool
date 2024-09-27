from os import path, remove as os_remove
from shutil import rmtree

from .exceptions import FileSystemError
from .verify import verify


def remove(source: str) -> None:
    try:
        if path.isdir(source):
            rmtree(source)

        elif path.isfile(source):
            os_remove(source)

    except Exception as e:
        pass