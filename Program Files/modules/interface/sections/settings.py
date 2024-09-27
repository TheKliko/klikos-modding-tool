from modules.interface import Window, get_foreground, Color
from modules.functions import settings


def run(window: Window) -> None:
    bad_input: bool = False
    while True:
        window.reset()
        window.change_section("Settings")

        try:
            data = settings.get_all()
        
        except Exception as e:
            window.add_line(f"{get_foreground(Color.WARNING)}\u26a0  Section failed to load!")
            window.add_line(f"{get_foreground(Color.ERROR)}{type(e).__name__}: {get_foreground(Color.WARNING)}{str(e)}")
            window.add_divider()
            window.press_x_to_y("ENTER", "return")
            return
        
        window.add_line(f"[{get_foreground(Color.NUMBER)}1{Color.RESET}]: {get_foreground(Color.ACTION)}Go Back")
        for i, setting in enumerate(data, 2):
            name = setting.get("name", None)
            value = setting.get("value", None)

            if value == True or value == False:
                value = f"{get_foreground(Color.ON)}+{Color.RESET}" if value == True else  f"{get_foreground(Color.OFF)}-{Color.RESET}"
            elif isinstance(value, int):
                value = f"{get_foreground(Color.NUMBER)}{value}{Color.RESET}"
            else:
                value = f"{get_foreground(Color.STRING)}{value}{Color.RESET}"
            
            window.add_line(f"[{get_foreground(Color.NUMBER)}{i}{Color.RESET}]: [{value}] {get_foreground(Color.ACTION)}{name}")
        window.add_divider()

        if bad_input == True:
            window.add_line(f"Bad input: \"{get_foreground(Color.ERROR)}{response}{Color.RESET}\"")
            window.add_line(f"Accepted responses are: [{get_foreground(Color.NUMBER)}1{Color.RESET}-{get_foreground(Color.NUMBER)}{len(data)+1}{Color.RESET}]")
            window.add_divider()

        window.update()

        response: str = window.get_input("Response: ")

        try:
            bad_input = False
            i = int(response)
            if i <= 0 or i > len(data)+1:
                raise Exception

        except:
            bad_input = True
            continue

        if i == 1:
            return
        
        configure(window, data[i-2])


def configure(window: Window, setting: dict) -> None:
    bad_input: bool = False
    while True:
        setting = settings.get(setting.get("name", setting))
        name = setting.get("name", None)
        description = setting.get("description", None)
        default = setting.get("default", None)
        setting_type = setting.get("type", None)
        value = setting.get("value", None)

        if value == True or value == False:
            value = f"{get_foreground(Color.ON)}enabled{Color.RESET}" if value == True else  f"{get_foreground(Color.OFF)}disabled{Color.RESET}"
        elif isinstance(value, int):
            value = f"{get_foreground(Color.NUMBER)}{value}{Color.RESET}"
        else:
            value = f"{get_foreground(Color.STRING)}\"{value}\"{Color.RESET}"

        window.reset()
        window.change_section("Settings", f" > {name}")
        window.add_line(f"{get_foreground(Color.SECTION_TITLE)}Setting: {name}")
        window.add_line(f"{get_foreground(Color.SECTION_TITLE)}Description: {description}")
        window.add_line(f"{get_foreground(Color.SECTION_TITLE)}Type: {str(setting_type).title()}")
        window.add_line(f"{get_foreground(Color.SECTION_TITLE)}Default: {default}")
        window.add_line(f"{get_foreground(Color.SECTION_TITLE)}Value: {value}")
        window.add_divider()

        options: list[str] = [
            "Go Back",
            "Set to Default"
        ]
        if setting_type == "choice":
            options += [f"Set value: {get_foreground(Color.STRING)}{option}" for option in setting.get("options", [])]
        elif setting_type == "boolean":
            options.append("Toggle status")
        elif isinstance(value, int):
            options.append("Change value")
        
        for i, option in enumerate(options, 1):
            window.add_line(f"[{get_foreground(Color.TRIGGER)}{i}{Color.RESET}]: {get_foreground(Color.ACTION)}{option}")
        window.add_divider()

        if bad_input == True:
            window.add_line(f"Bad input: \"{get_foreground(Color.ERROR)}{response}{Color.RESET}\"")
            window.add_line(f"Accepted responses are: [{get_foreground(Color.NUMBER)}1{Color.RESET}-{get_foreground(Color.NUMBER)}{len(options)}{Color.RESET}]")
            window.add_divider()

        response: str = window.get_input("Response: ")

        try:
            bad_input = False
            i = int(response)
            if i <= 0 or i > len(options):
                raise Exception

        except:
            bad_input = True
            continue

        if i == 1:
            return
        
        elif i == 2:
            settings.set(setting, setting.get("default", None))
            continue

        if setting_type == "choice":
            i -= 3
            value = [option for option in setting.get("options", [])][i]
            settings.set(setting, value)

        elif setting_type == "boolean":
            settings.set(setting, not value)

        elif setting_type == "integer":
            raise NotImplementedError("settings.configure(@line_135): elif setting_type == \"integer\"")