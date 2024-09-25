from os import path, makedirs

from .exceptions import FileSystemError


def verify(filepath: str, create_missing_directories: bool = False, create_missing_file: bool = False) -> None:
    if not path.exists(filepath):
        if create_missing_directories == False and create_missing_file == False:
            raise FileSystemError(f'Path does not exist: {filepath}')
        
        makedirs(filepath, exist_ok=True)
        
        if create_missing_file == True:
            with open(filepath, 'w') as file:
                file.close()