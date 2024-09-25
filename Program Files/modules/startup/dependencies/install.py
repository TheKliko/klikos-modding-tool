from os import path
from subprocess import check_call, CalledProcessError, PIPE
from sys import executable

from modules.interface import Color, print
from modules.filesystem import verify, Path

from .exceptions import DependencyError

IMPORT_MAP: dict = {
    "PIL": "pillow"
}


def install(library: str, is_version_specific: bool = False) -> None:

    library_directory: str = path.join(Path.libraries())
    version_specific_library_directory: str = path.join(Path.version_specific_libraries())
    
    verify(library_directory, create_missing_directories=True)
    verify(version_specific_library_directory, create_missing_directories=True)

    install_path: str = library_directory if is_version_specific == False else version_specific_library_directory
    
    try:
        print(f"  Installing dependency: {library}", color=Color.WARNING)
        check_call([executable, "-m", "pip", "install", "--target", install_path, "--upgrade", IMPORT_MAP.get(library.lower(), library)], stdin=PIPE, stdout=PIPE)
    except CalledProcessError as e:
        raise DependencyError(f"[{type(e).__name__}] Failed to install dependency: {str(e)}")