from json import load
from os import path

from modules.interface import Color, print

from .is_installed import is_installed
from .install import install
from .check_version_specific_libraries import check_version_specific_libraries


def check() -> None:
    try:
        print('Checking dependencies . . .', color=Color.INITALIZE)

        with open(path.join(path.dirname(__file__), 'requirements.json'), 'r') as file:
            data: dict = load(file)
            file.close()

        normal: list[str] = data.get('normal', [])
        version_specific: list[str] = data.get('version_specific', [])


        for library in normal:
            if is_installed(library) == False:
                install(library)
            else:
                continue

        check_version_specific_libraries(version_specific)
    
    except Exception as e:
        pass