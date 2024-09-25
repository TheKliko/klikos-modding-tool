from os import path, listdir, rmdir, makedirs
from importlib.util import find_spec

from modules.filesystem import Path

from .install import install


IMPORT_MAP: dict = {
    'pillow': 'PIL'
}


def check_version_specific_libraries(version_specific_libraries: list[str]) -> None:
    version_specific_library_directory: str = Path.version_specific_libraries()
        
    if not path.isdir(version_specific_library_directory):
        makedirs(version_specific_library_directory)

    for library in version_specific_libraries:
        if not find_spec(IMPORT_MAP.get(library.lower(), library)):
            install(library, is_version_specific=True)

    try:
        if listdir(version_specific_library_directory) == []:
            rmdir(version_specific_library_directory)
            if listdir(path.dirname(version_specific_library_directory)) == []:
                rmdir(path.dirname(version_specific_library_directory))

    except Exception as e:
        pass