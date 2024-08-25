# The third iteration of my Roblox mod updater
# Capable of updating any mod made for versions released after 16/3/2022 (dd/mm/yyyy)
#
# Shoutout to @nexx for suggesting an improved method of matching the image atlas
# (Comparing the git hash, instead of comparing every single pixel of each ImageSet)
# Which brought down the time spent matching ImageSets from minutes to less than 3 seconds

import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, 'Program Files', 'libraries'))

from modules import mod
from modules.roblox import version, icons


def main() -> None:
    try:
        temp_folder: str = os.path.join(ROOT, 'temp')

        # In case the temporary folder didn't get deleted due to the user manually closing the terminal
        if os.path.exists(temp_folder):
            print('Removing temporary files . . .')
            delete_directory(temp_folder)

        # Get Roblox versions
        print('Please select the mod that you wish to update!')
        mod_path = mod.get()
        roblox_mod_version: str = mod.version(mod_path)
        roblox_player_version: str = version.latest()

        print('Getting deployment history . . .')
        deploy_history: list[str] = version.deploy_history()
        studio_deploy_history: list[str] = []
        player_deploy_history: list[str] = []

        for line in deploy_history:
            if line.lower().startswith('new studio') and line not in studio_deploy_history:
                studio_deploy_history.append(line)
            elif line.lower().startswith('new windowsplayer') and line not in player_deploy_history:
                player_deploy_history.append(line)

        # Get Roblox Player git hashes
        print('Getting git hashes . . .')
        latest_roblox_git_hash: str = None
        modded_roblox_git_hash: str = None
        for line in player_deploy_history:
            version_guid: str = line.split(' ')[2]
            if version_guid == roblox_player_version and not latest_roblox_git_hash:
                git_hash: str = line.removesuffix(' ...').split(' ')[-1]
                latest_roblox_git_hash = git_hash

            if version_guid == roblox_mod_version and not modded_roblox_git_hash:
                git_hash: str = line.removesuffix(' ...').split(' ')[-1]
                modded_roblox_git_hash = git_hash

            if latest_roblox_git_hash and modded_roblox_git_hash:
                break
        
        # Make sure the git hashes exist
        if not latest_roblox_git_hash:
            raise Exception('latest_roblox_git_hash == None')
        if not modded_roblox_git_hash:
            raise Exception('modded_roblox_git_hash == None')
        
        print(f'[Latest]: {roblox_mod_version} -> {modded_roblox_git_hash}')
        print(f'[Modded]: {roblox_player_version} -> {latest_roblox_git_hash}')

        
        # Check if mod is already updated
        if roblox_player_version == roblox_mod_version or latest_roblox_git_hash == modded_roblox_git_hash:
            raise Exception('Mod is already updated')

        # Install versions of both the modded version and the latest release
        # Only installs extracontent-luapackages.zip to save storage space
        print()
        print(f'Downloading ImageSets . . .')
        version.installer(ROOT, roblox_mod_version, temp_folder)
        version.installer(ROOT, roblox_player_version, temp_folder)

    
        # The day before making this program, Roblox decided to move the Imagesets from /UIBlox/UIBlox/AppImageAtlas to /FoundationImages/FoundationImages/SpriteSheets
        # So I store both paths and check both paths for cross compatibility
        install_path: str = temp_folder
        path_to_image_atlas_old: str = os.path.join('ExtraContent', 'LuaPackages', 'Packages', '_Index', 'UIBlox', 'UIBlox', 'AppImageAtlas')
        path_to_image_atlas_new: str = os.path.join('ExtraContent', 'LuaPackages', 'Packages', '_Index', 'FoundationImages', 'FoundationImages', 'SpriteSheets')
        
        possible_mod_paths: list[str] = [
            os.path.join(mod_path, path_to_image_atlas_old),
            os.path.join(mod_path, path_to_image_atlas_new)
        ]
        possible_paths_player: list[str] = [
            os.path.join(install_path, roblox_player_version, path_to_image_atlas_old),
            os.path.join(install_path, roblox_player_version, path_to_image_atlas_new)
        ]


        # Compare git hashes to see which Studio version shares the same ImageSets as the modded and latest Roblox version
        # Required since the file that has every icon mapped out (GetImageSetData.lua) is deployed only with Roblox Studio
        print()
        print('Matching git hashes with Roblox Studio deployments . . .')
        player_studio_version: str = None
        modded_studio_version: str = None
        for i, line in enumerate(studio_deploy_history):
                git_hash: str = line.removesuffix(' ...').split(' ')[-1]
                version_guid: str = line.split(' ')[2]
                if git_hash == latest_roblox_git_hash and not player_studio_version:
                    player_studio_version = version_guid
                    print(f'[Latest]: {roblox_player_version} ({latest_roblox_git_hash}) -> {player_studio_version} ({git_hash})')
                if git_hash == modded_roblox_git_hash and not modded_studio_version:
                    modded_studio_version = version_guid
                    print(f'[Modded]: {roblox_mod_version} ({modded_roblox_git_hash}) -> {modded_studio_version} ({git_hash})')

                if player_studio_version and modded_studio_version:
                    break

                check_iteration_count(i)
                # If 100 iterations have occured, ask for confirmation to continue
                # This shouldn't normally happen, unless:
                #   - Your mod is *very* outdated
                #   - A matching Studio doesn't exit (yet).
                #      - Usually Studio versions get deployed a few minutes after Roblox Player version
                #   - Roblox randomly decided to stop uploading new Studio deployments to https://setup.rbxcdn.com/DeployHistory.txt
                #      - This is almost certainly not going to be the case

        else:  # Just in case
            raise Exception('Failed to match Studio versions')


        print()
        print(f'Downloading ImageSets . . .')
        version.installer(ROOT, player_studio_version, temp_folder)
        version.installer(ROOT, modded_studio_version, temp_folder)


        # Get icon data
        base_path_old: str = os.path.join(install_path, modded_studio_version)
        base_path_new: str = os.path.join(install_path, player_studio_version)
        path_to_image_data_old: str = os.path.join(os.path.dirname(path_to_image_atlas_old), 'App', 'ImageSet', 'GetImagesetData.lua')
        path_to_image_data_new: str = os.path.join(os.path.dirname(path_to_image_atlas_new), 'Generated', 'GetImagesetData.lua')
        imagesetdata_paths_old: list[str] = [
            os.path.join(base_path_old, path_to_image_data_old),
            os.path.join(base_path_old, path_to_image_data_new)
        ]
        imagesetdata_paths_new: list[str] = [
            os.path.join(base_path_new, path_to_image_data_old),
            os.path.join(base_path_new, path_to_image_data_new)
        ]
        print()
        print('Getting icon data . . .')
        icon_map_old: dict = icons.get_icon_map(imagesetdata_paths_old)
        icon_map_new: dict = icons.get_icon_map(imagesetdata_paths_new)


        # Check which icons are modded
        print('Getting modded icons . . .')
        possible_paths_modded_studio: list[str] = [
            os.path.join(install_path, modded_studio_version, path_to_image_atlas_old),
            os.path.join(install_path, modded_studio_version, path_to_image_atlas_new)
        ]
        modded_icons: dict = icons.get_modded_icons(icon_map_old, possible_mod_paths, possible_paths_modded_studio)


        # Generate new ImageSets
        print('Generating new ImageSets . . .')
        icons.generate_imagesets(icon_map_old, icon_map_new, modded_icons, possible_mod_paths, [path.replace(roblox_player_version, player_studio_version) for path in possible_paths_player], os.path.join(install_path, 'updated_atlas'))


        # Copy the mod and update info.json
        print('Copying mod . . .')
        new_path: str = os.path.join(ROOT, f'{os.path.basename(mod_path)}_updated')
        if os.path.exists(new_path):
            shutil.rmtree(new_path)
        shutil.copytree(mod_path, new_path)

        print('Updating info.json . . .')
        with open(os.path.join(new_path, 'info.json'),'r') as file:
            data = json.load(file)
            file.close()
        data['clientVersionUpload'] = roblox_player_version
        with open(os.path.join(new_path, 'info.json'),'w') as file:
            json.dump(data, file, indent=4)
            file.close()


        # Replace old ImageSets with the new ones
        print('Replacing old ImageSets . . .')
        atlas_path_1: str = os.path.join(new_path, path_to_image_atlas_old)
        atlas_path_2: str = os.path.join(new_path, path_to_image_atlas_new)
        shutil.rmtree(atlas_path_1, ignore_errors=True)
        shutil.rmtree(atlas_path_2, ignore_errors=True)
        shutil.copytree(os.path.join(install_path, 'updated_atlas'), atlas_path_2)

        # Delete UIBlox/UIBlox if empty
        # Only happens when updating mods from the old format: `UIBlox/UIBlox/AppImageAtlas`
        # To the new format: `FoundationImages/FoundationImages/SpriteSheets`
        uiblox: str = os.path.dirname(os.path.dirname(atlas_path_1))
        if os.path.exists(uiblox):
            for dirpath, dirnames, filenames in os.walk(uiblox):
                if not filenames:
                    shutil.rmtree(dirpath)
                    break


        # Delete temporary files
        print('Removing temporary files . . .')
        delete_directory(temp_folder)
        print()
        print(f'`{os.path.basename(mod_path)}` has been updated to {roblox_player_version} ({latest_roblox_git_hash})')


    except Exception as e:
        print(f'An unexpected {type(e).__name__} occured: {str(e)}')
        delete_directory(temp_folder)


def check_iteration_count(iteration: int) -> None:
    if iteration % 100 == 0 and iteration != 0:
        print()
        print(f'{iteration} versions have been checked, but no match was found (yet).')
        print('Do you still wish to continue? [Y/N]')
        response = input('response: ')
        if response.lower() not in ['y', 'yes', 'sure', 'ok']:
            raise Exception('Manual quit-out')


def delete_directory(path) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.isfile(path):
        os.remove(path)


if __name__ == '__main__':
    main()
    input('Press ENTER to exit . . .')