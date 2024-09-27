from tempfile import TemporaryDirectory
from os import path, sep, walk
from shutil import copytree, copy2
import time
import json

from modules.api import RobloxApi
from modules.interface import Window, get_foreground, Color
from modules.filesystem import download, extract, remove
from modules.functions import settings, roblox, mods

from PIL import Image, ImageColor, PngImagePlugin


ICON_BLACKLIST_FALLBACK: list[str] = [
    "component_assets/circle_17_mask",
    "component_assets/contactFullAvatar_large",
    "component_assets/contactHeadshot",
    "icons/graphic/error_xlarge",
    "icons/graphic/newclothing_xlarge",
    "icons/graphic/success_xlarge",

    "component_assets/avatarBG_dark",
    "component_assets/user_60_mask"
    "component_assets/contactFullAvatar_small",
    "component_assets/profileHeaderBG",

    "component_assets/avatarBG_light",
    "component_assets/circle_49_mask",

    "component_assets/itemBG_light",
    "icons/graphic/robuxcoin1_xxlarge",
    "icons/graphic/robuxcoin2_xxlarge",
    "icons/graphic/robuxcoin3_xxlarge",

    "component_assets/circle_29_mask",
    "component_assets/itemBG_dark",
    "icons/graphic/newclothing_3xl",
    "icons/graphic/robuxcoin5_xxlarge",
    "icons/graphic/robuxcoin6_xxlarge",

    "component_assets/vignette_246",
    "icons/graphic/robuxcoin4_xxlarge"
]



def run(window: Window) -> None:
    mode: str = settings.get("mod generator").get("value", None).lower()

    bad_input: bool = False
    while True:
        window.reset()
        window.change_section("Mod Generator", f"Mode: {mode.title()}")

        window.add_line("To return, type \"1\"")


        
        if mode.lower() == "color":
            window.add_line("Choose a color")
        
        elif mode.lower() == "gradient":
            window.add_line("Choose a gradient in the following format: \"color_1 -> color_2\"")


        if bad_input == True:
            window.add_line(f"Bad input: \"{get_foreground(Color.ERROR)}{response}{Color.RESET}\"")
            
            if mode.lower() == "color":
                window.add_line("Response must be a color!")
            elif mode.lower() == "gradient":
                window.add_line("Response must be a gradient in the following format: \"color_1 -> color_2\"!")

        window.add_divider()

        window.update()

        response: str = window.get_input("Response: ")

        if response == "1":
            return

        if mode.lower() == "color":
            try:
                color = ImageColor.getcolor(response, "RGB")
            except:
                try:
                    color = ImageColor.getcolor(f"#{response}", "RGB")
                except:
                    bad_input = True
                    continue
            
            generate_mod(window, mode, color)
            return


        if mode.lower() == "gradient":
            try:
                colors: list[str] = response.split(" -> ")
                color1: str = colors[0]
                color2: str = colors[1]
            except:
                bad_input = True
                continue
            try:
                color1 = ImageColor.getcolor(color1, "RGB")
            except:
                try:
                    color1 = ImageColor.getcolor(f"#{color1}", "RGB")
                except:
                    bad_input = True
                    continue
            try:
                color2 = ImageColor.getcolor(color2, "RGB")
            except:
                try:
                    color2 = ImageColor.getcolor(f"#{color2}", "RGB")
                except:
                    bad_input = True
                    continue
            
            generate_mod(window, mode, color1, color2)
            return


def generate_mod(window: Window, mode: str, color, color2 = None) -> None:
    description: str = f"Generating mod: {f'rgb{color}' if color2 is None else f'rgb{color} -> rgb{color2}'}"
    mod_name: str = f"klikos-mod-generator-{str(int(time.time()))}"

    window.reset()
    window.change_section("Mod Generator", description)

    window.update()
    
    channel: str = settings.get("channel").get("value", "LIVE")
    if channel.lower() == "auto":
        channel = roblox.get_user_channel()
    version = roblox.get_latest_version(channel)

    window.add_line(f"{get_foreground(Color.INFO)}Version: {version}, Channel: {channel}")
    window.add_divider()
    window.update()
    
    deploy_history = roblox.DeployHistory()
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

    window.remove_last()
    window.add_line(f"{get_foreground(Color.INFO)}Matching Studio version: {version_latest_studio}")
    window.add_divider()
    window.update()


    with TemporaryDirectory() as temp_directory:
        window.remove_last()
        window.add_line(f"{get_foreground(Color.INFO)}Downloading LuaPackages . . .")
        window.add_divider()
        window.update()

        download_url: str = RobloxApi.download(version_latest_studio, "extracontent-luapackages.zip")
        download(download_url, path.join(temp_directory, "extracontent-luapackages.zip"))
        extract(path.join(temp_directory, "extracontent-luapackages.zip"), path.join(temp_directory, version_latest_studio, "ExtraContent", "LuaPackages"))
        remove(path.join(temp_directory, "extracontent-luapackages.zip"))
        
        window.remove_last()
        window.add_line(f"{get_foreground(Color.INFO)}Locating ImageSets . . .")
        window.add_divider()
        window.update()

        for dirpath, _, filenames in walk(temp_directory):
            if "GetImageSetData.lua" in filenames:
                relative_path: str = path.join(path.relpath(path.join(dirpath, "GetImageSetData.lua"), temp_directory))
                imagesetdata_filepath: str = sep.join(relative_path.split(sep)[1:])
                break
        else:
            raise Exception("Failed to locate GetImageSetData.lua")

        for dirpath, _, filenames in walk(temp_directory):
            if "img_set_1x_1.png" in filenames:
                relative_path: str = path.dirname(path.join(path.relpath(path.join(dirpath, "GetImageSetData.lua"), temp_directory)))
                imageset_path: str = sep.join(relative_path.split(sep)[1:])
                break
        else:
            raise Exception("Failed to locate ImageSets!")


        window.remove_last()
        window.add_line(f"{get_foreground(Color.INFO)}Extracting icon data . . .")
        window.add_divider()
        window.update()

        icon_map: dict[str,dict[str,dict[str,str|int]]] = mods.get_icon_map(temp_directory, imagesetdata_filepath, version_latest_studio)

        window.remove_last()
        window.add_line(f"{get_foreground(Color.INFO)}Generating ImageSets . . .")
        window.add_divider()
        window.update()

        generate_imagesets(mod_name, icon_map, imageset_path, version_latest_studio, temp_directory, color, color2)
        
        window.remove_last()
        window.add_line(f"{get_foreground(Color.INFO)}Finishing mod . . .")
        window.add_divider()
        window.update()

        add_info_file(temp_directory, mod_name, version)

        root: str = path.dirname(path.dirname(path.dirname(path.dirname(path.dirname(__file__)))))
        copytree(path.join(temp_directory, mod_name), path.join(root, "Generated mods", mod_name), dirs_exist_ok=True)
    
    window.add_line(f"{get_foreground(Color.ON)}Mod generated successfully!")
    window.add_divider()
    window.press_x_to_y("ENTER", "return")


def generate_imagesets(name: str, icon_map: dict[str,dict[str,dict[str,str|int]]], imageset_path: str, version: str, temp_directory: str, color, color2 = None):
    try:
        blacklist_file: str = path.join(path.dirname(__file__), "mod_generator_files", "blacklist.json")
        with open(blacklist_file, "r") as file:
            blacklist = json.load(file)
    except:
        blacklist = ICON_BLACKLIST_FALLBACK
    
    path_to_imagesets: str = path.join(temp_directory, name, imageset_path)
    path_to_unmodded_imagesets: str = path.join(temp_directory, version, imageset_path)

    copytree(path_to_unmodded_imagesets, path_to_imagesets, dirs_exist_ok=True)
    Image.open(path.join(path.dirname(__file__), "mod_generator_files", "watermark.png")).save(path.join(path_to_imagesets, "watermark.png"))

    for size in icon_map.keys():
        for icon in icon_map[size].keys():
            if icon in blacklist:
                continue

            icon_data: dict = icon_map[size][icon]

            imageset: str = icon_data["set"]
            x: int = icon_data["x"]
            y: int = icon_data["y"]
            w: int = icon_data["w"]
            h: int = icon_data["h"]

            image_path: str = path.join(path_to_imagesets, f"{imageset}.png")
            image: Image.Image = Image.open(image_path)
            modded_icon: Image.Image = image.crop((x,y,x+w,y+h))

            mask: Image.Image = get_mask(w, h, color, color2)
            
            alpha = modded_icon.split()[3]
            modded_icon = Image.composite(mask, modded_icon, alpha)
            modded_icon.putalpha(alpha)
            
            image.paste(modded_icon, (x,y))

            if image.format == "PNG":
                image.save(image_path, format=image.format, pnginfo=get_png_info(image))
            image.save(image_path)


def get_mask(width: int, height: int, color, color2 = None) -> Image:
    mask: Image.Image = Image.new("RGBA", (width,height), color)
    if color2 is not None:
        for x in range(width):
            r = int(color[0] + (color2[0] - color[0]) * (x / float(width)))
            g = int(color[1] + (color2[1] - color[1]) * (x / float(width)))
            b = int(color[2] + (color2[2] - color[2]) * (x / float(width)))
            
            for y in range(height):
                mask.putpixel((x, y), (r, g, b))
    return mask


def get_png_info(image: Image.Image) -> PngImagePlugin.PngInfo:
    return PngImagePlugin.PngInfo().add_text("Comment", "Generated by Kliko's Modding Tool")


def add_info_file(temp_directory: str, mod: str, version: str) -> None:
    filepath: str = path.join(temp_directory, mod, "info.json")
    data: dict = {
        "clientVersionUpload": version,
        "watermark": "Mod generated by Kliko's Modding Tool"
    }
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)