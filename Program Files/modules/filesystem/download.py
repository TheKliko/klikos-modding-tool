from os import path
from urllib.request import urlretrieve

from .verify import verify
from .exceptions import FileSystemError


def download(url: str, destination: str) -> None:
    try:
        verify(path.dirname(destination), create_missing_directories=True)
        urlretrieve(url, destination)

    except Exception as e:
        raise FileSystemError(f'[{type(e).__name__}] {str(e)}')