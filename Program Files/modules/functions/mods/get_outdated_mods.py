from os import path
from json import load


def get_outdated_mods(version: str, mods: list[str]) -> dict[str, list[str]]:
    outdated_mods: dict[str, list[str]] = {}
    for mod in mods:
        mod_info_path: str = path.join(mod, 'info.json')
        if not path.isfile(mod_info_path):
            continue

        with open(mod_info_path, 'r') as file:
            data: dict = load(file)
        
        mod_version: str = data.get('clientVersionUpload', None)
        if mod_version is None:
            continue
        elif mod_version == version:
            continue

        if outdated_mods.get(mod_version, None) is None:
            outdated_mods[mod_version] = [mod]
        else:
            outdated_mods[mod_version].append(mod)
    
    return outdated_mods