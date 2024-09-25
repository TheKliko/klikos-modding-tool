from zipfile import ZipFile

from .verify import verify
from .exceptions import FileSystemError


def extract(source: str, destination: str) -> None:
    try:
        verify(source)
        verify(destination, create_missing_directories=True)
        
        with ZipFile(source, 'r') as zip:
            zip.extractall(destination)
            zip.close()

    except Exception as e:
        raise FileSystemError(f'[{type(e).__name__}] {str(e)}')