from json import load, dump
from os import path, listdir, walk, makedirs
from shutil import rmtree, copytree


def update(mods: list[str], temp_directory: str, latest_version: str) -> None:
    for mod in mods:
        base_path: str = mod
        mod: str = path.basename(mod)
        source: str = path.join(temp_directory, mod)

        path_to_mod_imagesets: str = None
        for dirpath, _, filenames in walk(base_path):
            for filename in filenames:
                if filename.startswith('img_set'):
                    path_to_mod_imagesets: str = dirpath
                    break
            if path_to_mod_imagesets != None:
                break

        rmtree(path_to_mod_imagesets, ignore_errors=True)
        will_think_of_a_name_later_path: str = path_to_mod_imagesets
        while True:
            will_think_of_a_name_later_path = path.dirname(will_think_of_a_name_later_path)
            if listdir(will_think_of_a_name_later_path) != []:
                break
            rmtree(will_think_of_a_name_later_path)

        copytree(source, base_path, dirs_exist_ok=True)

        with open(path.join(base_path, 'info.json'), 'r') as file:
            data: dict = load(file)
            file.close()

        data['clientVersionUpload'] = latest_version

        with open(path.join(base_path, 'info.json'), 'w') as file:
            dump(data, file)
            file.close()


def update_paranoid(mods: list[str], temp_directory: str, latest_version: str, root: str) -> None:
    for mod in mods:
        base_path: str = mod
        mod: str = path.basename(mod)
        source: str = path.join(temp_directory, mod)

        updated_base_path: str = path.join(root, "Updated Mods", f"{mod}_updated")

        input(updated_base_path)
        copytree(base_path, path.join(root, updated_base_path))

        path_to_mod_imagesets: str = None
        for dirpath, _, filenames in walk(updated_base_path):
            for filename in filenames:
                if filename.startswith('img_set'):
                    path_to_mod_imagesets: str = dirpath
                    break
            if path_to_mod_imagesets != None:
                break

        rmtree(path_to_mod_imagesets, ignore_errors=True)
        remove_this_directory_if_empty: str = path_to_mod_imagesets
        while True:
            remove_this_directory_if_empty = path.dirname(remove_this_directory_if_empty)
            if listdir(remove_this_directory_if_empty) != []:
                break
            rmtree(remove_this_directory_if_empty)

        copytree(source, path.join(root, updated_base_path), dirs_exist_ok=True)

        with open(path.join(path.join(root, updated_base_path), 'info.json'), 'r') as file:
            data: dict = load(file)
            file.close()

        data['clientVersionUpload'] = latest_version

        with open(path.join(path.join(root, updated_base_path), 'info.json'), 'w') as file:
            dump(data, file)
            file.close()