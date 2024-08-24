import os
import shutil
import zipfile

import requests
import urllib.request


def installer(root: str, version: str, temp_folder: str) -> None:  # Modified to only install extracontent-luapackages.zip
    install_directory: str = os.path.join(temp_folder, version)
    extraction_map: dict = {
        'extracontent-luapackages.zip': os.path.join('ExtraContent', 'LuaPackages')
    }

    def get_base_url(version: str, channel: str = 'live') -> str:
        base: str = r'https://setup.rbxcdn.com/'
        version_id: str = version if version.startswith('version-') else f'version-{version}'
        url: str = f'{base}{version_id}-'
        return url

    def download_file(base_url: str, filename: str, target_directory: str) -> None:
        if not filename in extraction_map.keys():
            print(f'Skipping file: {filename}')
            return

        if not os.path.isdir(target_directory):
            os.makedirs(target_directory)

        url: str = f'{base_url}{filename}'
        target: str = os.path.join(target_directory, filename)
        urllib.request.urlretrieve(url, target)

    def install_files(download_directory: str, target_directory: str) -> None:
        if not os.path.isdir(target_directory):
            os.makedirs(target_directory)

        files_to_extract = [file for file in os.listdir(download_directory) if file.endswith('.zip')]

        for file in files_to_extract:
            try:
                path_extension: str = extraction_map.get(file, r'{ROOT}')
                target: str = os.path.join(target_directory, path_extension) if path_extension != r'{ROOT}' else target_directory
            except:
                print(f'Skipping file: {file}')
                continue

            print(f'Extracting {file} . . .')
            with zipfile.ZipFile(os.path.join(download_directory, file), 'r') as zip:
                zip.extractall(target)
                zip.close()

    def cleanup(file) -> None:
        if os.path.isfile(file):
            os.remove(file)


    try:
        url: str = get_base_url(version)
        file = 'extracontent-luapackages.zip'
        print(f'Downloading {file} . . .')
        download_file(url, file, temp_folder)
        install_files(temp_folder, install_directory)
        cleanup(os.path.join(temp_folder, file))

    except Exception as e:
        print(f'An unexpected {type(e).__name__} occured: {str(e)}')


def latest(mode: str = 'windowsplayer') -> str:
    """Return the version ID of the latest Roblox version"""

    base1: str = r'https://clientsettingscdn.roblox.com/v2/client-version/'
    base2: str = r'/channel/live'
    url: str = rf'{base1}{mode}{base2}'
    response = requests.get(url)
    response.raise_for_status()
    version: str = response.json()['clientVersionUpload']
    return version


def deploy_history(studio_only: bool = False) -> list[str]:
    url: str = r'https://setup.rbxcdn.com/DeployHistory.txt'
    response = requests.get(url)
    response.raise_for_status()

    if studio_only == True:
        return [line for line in reversed(response.text.splitlines()) if line.lower().startswith('new studio')]

    return [line for line in reversed(response.text.splitlines())]


def main() -> None:
    print('version.py')
    print('module used in Kliko\'s mod updater')
    input('Press ENTER to exit . . .')


if __name__ == '__main__':
    main()