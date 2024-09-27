from modules.filesystem import Path, verify, FileSystemError
from modules.interface import print, Color

from .exceptions import CoreFilesMissing


def check_core_files() -> None:
    try:
        print("Checking core files . . .", color=Color.INITALIZE)
        verify(Path.settings())
    
    except FileSystemError as e:
        raise CoreFilesMissing("Please reinstall this program!")