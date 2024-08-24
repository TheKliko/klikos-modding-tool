import json
import os

from pathlib import Path
from tkinter.filedialog import askdirectory


def get() -> Path:
    default: str = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    directory: str = askdirectory(initialdir=default, title='Select your mod')
    return Path(directory)


def version(path_to_mod_directory) -> str:
    try:
        with open(os.path.join(path_to_mod_directory, 'info.json')) as file:
            config = json.load(file)
            file.close()
        return config['clientVersionUpload']

    except Exception as e:
        raise Exception(f'[mod.version] {type(e).__name__}: {str(e)}')


def main() -> None:
    print('version.py')
    print('module used in Kliko\' s mod updater')
    input('Press ENTER to exit . . .')


if __name__ == '__main__':
    main()