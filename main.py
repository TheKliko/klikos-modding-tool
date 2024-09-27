import os
import sys

root: str = os.path.join(os.path.dirname(__file__))
program_files: str = os.path.join(root, "Program Files")
sys.path.append(program_files)

from modules.filesystem.paths import Path

libraries: str = Path.libraries()
version_specific_libraries: str = Path.version_specific_libraries()
sys.path.append(libraries)
sys.path.append(version_specific_libraries)

try:
    os.makedirs(libraries, exist_ok=True)
    os.makedirs(version_specific_libraries, exist_ok=True)
except:
    pass


from modules import interface
from modules import startup
from modules.exception_handler import exception_handler


WELCOME_MESSAGE: str = r"""
 _   ___ _ _         _      ___  ___          _     _ _               _____           _ 
| | / / (_) |       ( )     |  \/  |         | |   | (_)             |_   _|         | |
| |/ /| |_| | _____ |/ ___  | .  . | ___   __| | __| |_ _ __   __ _    | | ___   ___ | |
|    \| | | |/ / _ \  / __| | |\/| |/ _ \ / _` |/ _` | | '_ \ / _` |   | |/ _ \ / _ \| |
| |\  \ | |   < (_) | \__ \ | |  | | (_) | (_| | (_| | | | | | (_| |   | | (_) | (_) | |
\_| \_/_|_|_|\_\___/  |___/ \_|  |_/\___/ \__,_|\__,_|_|_| |_|\__, |   \_/\___/ \___/|_|
                                                               __/ |                    
                                                              |___/                     
"""  # ASCII art generated at https://www.patorjk.com/software/taag/


def main() -> None:
    window = interface.Window()
    try:
        interface.clear()
        interface.print()
        interface.print(WELCOME_MESSAGE, color=interface.Color.SPLASH, alignment=interface.Alignment.CENTER)
        startup.run()

        from modules.interface import sections

        options: list[str] = [
            "Exit",
            "Update Mods",
            f"Mod Generator {interface.get_foreground(interface.Color.WARNING)}[EXPERIMENTAL]",
            "Settings"
        ]
        bad_input: bool = False
        while True:
            window.change_section("Welcome,", "Please choose an option to get started!")
            window.reset()
            for i, option in enumerate(options, 1):
                window.add_line(f"[{interface.get_foreground(interface.Color.NUMBER)}{i}{interface.Color.RESET}]: {interface.get_foreground(interface.Color.ACTION)}{option}{interface.Color.RESET}")
            window.add_divider()

            if bad_input == True:
                window.add_line(f"Bad input: \"{interface.get_foreground(interface.Color.ERROR)}{response}{interface.Color.RESET}\"")
                window.add_line(f"Accepted responses are: [{interface.get_foreground(interface.Color.NUMBER)}1{interface.Color.RESET}-{interface.get_foreground(interface.Color.NUMBER)}{len(options)}{interface.Color.RESET}]")
                window.add_divider()

            window.update()

            response = window.get_input("Response: ")

            try:
                bad_input = False
                i = int(response)
                if i <= 0 or i > len(options):
                    raise Exception

            except:
                bad_input = True
                continue
                
            if i == 1:
                break
                
            elif i == 2:
                sections.mod_updater.run(window)
            
            elif i == 3:
                sections.mod_generator.run(window)
            
            elif i == 4:
                sections.settings.run(window)

    except Exception as e:
        exception_handler(window, e)
    
    sys.exit()


if __name__ == "__main__":
    main()