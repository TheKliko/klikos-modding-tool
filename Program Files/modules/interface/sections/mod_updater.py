from os import path, getenv, listdir, sep, walk
from tempfile import TemporaryDirectory
from tkinter.filedialog import askdirectory

from modules.api import RobloxApi
from modules.interface import Window, get_foreground, Color
from modules.filesystem import download, extract, remove
from modules.functions import settings
from modules.functions import roblox, mods

def run(window: Window) -> None:
    window.reset()
    window.change_section("Mod Updater")

    window.update()

    mode: str = settings.get("mode").get("value", None)
    localappdata = getenv("LOCALAPPDATA")
    if mode.lower() == "bloxstrap" and localappdata is not None:
        mods_to_update: list = [path.join(localappdata, "Bloxstrap", "Modifications")]
    
    else:
        window.add_line("Please select the mod(s) you want to update!")
        window.add_divider()
        window.update()
        mods_to_update: list = [askdirectory()]
        if mode.lower() == "batch" or mode.lower() == "batch_paranoid":
            mods_to_update = [path.join(mods_to_update[0], directory) for directory in listdir(str(mods_to_update[0])) if path.isdir(path.join(mods_to_update[0], directory))]

    channel: str = settings.get("channel").get("value", None)
    if channel.lower() == "auto" or channel is None:
        channel = roblox.get_user_channel()
    
    version = roblox.get_latest_version(channel)
    outdated_mods: dict[str,list[str]] = mods.get_outdated_mods(version, mods_to_update)
    number_of_outdated_mods: int = len([mod for mods in outdated_mods.values() for mod in mods])

    if number_of_outdated_mods == 0:
        raise Exception("No outdated mods could be found.")

    window.reset()
    window.add_line(f"{get_foreground(Color.SECTION_TITLE)}Updating {get_foreground(Color.NUMBER)}{number_of_outdated_mods} {get_foreground(Color.SECTION_TITLE)}mod{"" if number_of_outdated_mods == 1 else "s"} . . .")
    window.add_line(f"{get_foreground(Color.SECTION_TITLE)}(This may take a few minutes)")
    window.add_divider()
    window.update()

    window.add_line(f"{get_foreground(Color.INFO)}Getting DeployHistory . . .")
    window.add_divider()
    window.update()
    deploy_history = roblox.DeployHistory()

    window.remove_last()
    window.add_line(f"{get_foreground(Color.INFO)}Matching git hashes . . .")
    window.add_divider()
    window.update()
    git_hash_latest: str = None
    for file in deploy_history.ROBLOX_PLAYER:
        if file["version"] == version:
            git_hash_latest = file["git_hash"]
            break
    if git_hash_latest is None:
        window.remove_last()
        window.add_line(f"{get_foreground(Color.ERROR)}Mod update failed: git_hash_latest is None")
        window.add_divider()
        window.press_x_to_y("ENTER", "return")
        return

    version_latest_studio: str = None
    for file in deploy_history.ROBLOX_STUDIO:
        if file["git_hash"] == git_hash_latest:
            version_latest_studio = file["version"]
            break
    if version_latest_studio is None:
        window.remove_last()
        window.add_line(f"{get_foreground(Color.ERROR)}Mod update failed: version_latest_studio is None")
        window.add_divider()
        window.press_x_to_y("ENTER", "return")
        return

    mod_versions_to_update: list[dict[str, str]] = []
    for mod_version in outdated_mods.keys():
        for file in deploy_history.ALL:
            if file["version"] == mod_version:
                git_hash = file["git_hash"]
                if git_hash != git_hash_latest and not file["version"] in mod_versions_to_update:
                    mod_versions_to_update.append({
                        "version": file["version"],
                        "git_hash": git_hash
                    })
    
    if mod_versions_to_update == []:
        window.remove_last()
        window.add_line(f"{get_foreground(Color.ERROR)}Mod update cancelled: All mods are already updated")
        window.add_divider()
        window.press_x_to_y("ENTER", "return")
        return


    with TemporaryDirectory() as temp_directory:
        window.remove_last()
        window.add_line(f"{get_foreground(Color.INFO)}Downloading LuaPackages . . .")
        window.add_divider()
        window.update()

        download_url: str = RobloxApi.download(version, "extracontent-luapackages.zip")
        download(download_url, path.join(temp_directory, "extracontent-luapackages.zip"))
        extract(path.join(temp_directory, "extracontent-luapackages.zip"), path.join(temp_directory, version, "ExtraContent", "LuaPackages"))
        remove(path.join(temp_directory, "extracontent-luapackages.zip"))

        download_url: str = RobloxApi.download(version_latest_studio, "extracontent-luapackages.zip")
        download(download_url, path.join(temp_directory, "extracontent-luapackages.zip"))
        extract(path.join(temp_directory, "extracontent-luapackages.zip"), path.join(temp_directory, version_latest_studio, "ExtraContent", "LuaPackages"))
        remove(path.join(temp_directory, "extracontent-luapackages.zip"))

        for mod_data in mod_versions_to_update:
            mod_version: str = mod_data["version"]
            download_url: str = RobloxApi.download(mod_version, "extracontent-luapackages.zip")
            download(download_url, path.join(temp_directory, "extracontent-luapackages.zip"))
            extract(path.join(temp_directory, "extracontent-luapackages.zip"), path.join(temp_directory, mod_version, "ExtraContent", "LuaPackages"))
            remove(path.join(temp_directory, "extracontent-luapackages.zip"))
        
            version_mod_studio: str = None
            for file in deploy_history.ROBLOX_STUDIO:
                if file["git_hash"] == mod_data["git_hash"]:
                    version_mod_studio = file["version"]
                    git_hash_mod_studio = file["git_hash"]
                    break
            if version_mod_studio is None:
                window.remove_last()
                window.add_line(f"{get_foreground(Color.ERROR)}Mod update failed: version_mod_studio is None")
                window.add_divider()
                window.press_x_to_y("ENTER", "return")
                return

            download_url: str = RobloxApi.download(version_mod_studio, "extracontent-luapackages.zip")
            download(download_url, path.join(temp_directory, "extracontent-luapackages.zip"))
            extract(path.join(temp_directory, "extracontent-luapackages.zip"), path.join(temp_directory, version_mod_studio, "ExtraContent", "LuaPackages"))
            remove(path.join(temp_directory, "extracontent-luapackages.zip"))

            
            window.remove_last()
            window.add_line(f"{get_foreground(Color.INFO)}Locating ImageSetData.lua . . .")
            window.add_divider()
            window.update()

            imagesetdata_filepaths: list[dict[str, str]] = []
            for dirpath, _, filenames in walk(temp_directory):
                if "GetImageSetData.lua" in filenames:
                    relative_path: str = path.join(path.relpath(path.join(dirpath, "GetImageSetData.lua"), temp_directory))
                    imagesetdata_filepaths.append({
                        "version": relative_path.split(sep)[0],
                        "path": sep.join(relative_path.split(sep)[1:])
                    })

            imageset_paths: list[dict[str, str]] = []
            for dirpath, _, filenames in walk(temp_directory):
                if "img_set_1x_1.png" in filenames:
                    relative_path: str = path.dirname(path.join(path.relpath(path.join(dirpath, "GetImageSetData.lua"), temp_directory)))
                    imageset_paths.append({
                        "version": relative_path.split(sep)[0],
                        "path": sep.join(relative_path.split(sep)[1:])
                    })


            window.remove_last()
            window.add_line(f"{get_foreground(Color.INFO)}Extracting icon data . . .")
            window.add_divider()
            window.update()

            icon_maps: dict[str,dict[str,dict[str,str|int]]] = mods.get_icon_maps(temp_directory, imagesetdata_filepaths)

            mods_for_this_version: list[str] = outdated_mods[mod_version]

            
            window.remove_last()
            window.add_line(f"{get_foreground(Color.INFO)}Detecting modded icons . . .")
            window.add_divider()
            window.update()

            modded_icons: dict[str,dict[str,list]] = mods.get_modded_icons(mods_for_this_version, imageset_paths, icon_maps, version_mod_studio, temp_directory)

            
            window.remove_last()
            window.add_line(f"{get_foreground(Color.INFO)}Generating ImageSets . . .")
            window.add_divider()
            window.update()

            mods.generate_imagesets(modded_icons, mods_for_this_version, imageset_paths, icon_maps, version_mod_studio, version_latest_studio, temp_directory)
            
            window.remove_last()
            window.add_line(f"{get_foreground(Color.INFO)}Finishing mod update . . .")
            window.add_divider()
            window.update()

            if mode.lower() == "paranoid" or mode.lower() == "batch_paranoid":
                root: str = path.dirname(path.dirname(path.dirname(path.dirname(path.dirname(__file__)))))
                mods.update_paranoid(mods_for_this_version, temp_directory, version, root)
            else:
                mods.update(mods_for_this_version, temp_directory, version)

            window.remove_last()
            window.add_line(f"{get_foreground(Color.INFO)}Removing temporary files . . .")
            window.add_divider()
            window.update()

    window.remove_last()
    window.add_line(f"{get_foreground(Color.ON)}Mod update complete!")
    window.add_divider()
    window.update()
    window.press_x_to_y("ENTER", "return")