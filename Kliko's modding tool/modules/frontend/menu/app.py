from typing import Literal, Any
from datetime import datetime
from threading import Thread
from tkinter import messagebox
import webbrowser
import os

from modules.project_data import ProjectData
from modules.localization import Localizer
from modules.logger import Logger
from modules.frontend.widgets import Root, Frame, Label, Button
from modules.filesystem import Resources
from modules.interfaces.config import ConfigInterface
from modules.networking import requests, Response, Api
from modules.frontend.functions import get_ctk_image

from .sections import ModUpdaterSection, ModGeneratorSection, ShortcutsSection, SettingsSection, AboutSection

from customtkinter import CTkImage  # type: ignore
from packaging.version import Version  # type: ignore


class App(Root):
    active_section: str = ""
    loaded_sections: dict = {}
    sidebar: Frame

    mod_updater_section: ModUpdaterSection
    mod_generator_section: ModGeneratorSection
    shortcuts_section: ShortcutsSection
    settings_section: SettingsSection
    about_section: AboutSection

    _NAV_ICON_SIZE: int = 24
    _SIDEBAR_MIN_WIDTH: int = 286
    _SIDEBAR_LOGO_SIZE: Any = ("auto", 48)


    def __init__(self) -> None:
        appearance: Literal["light", "dark", "system"] = ConfigInterface.get_appearance_mode()
        width, height = ConfigInterface.get_menu_size()
        super().__init__(title=ProjectData.NAME, icon=Resources.FAVICON, appearance_mode=appearance, width=width, height=height, centered=True, banner_system=True)
        self.grid_columnconfigure(0, minsize=self._SIDEBAR_MIN_WIDTH)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Check for updates (async)
        if ConfigInterface.get("check_for_updates"):
            Thread(target=self._check_for_updates, daemon=True).start()

        # Create sidebar
        self.sidebar: Frame = Frame(self, transparent=True)
        self.configure_sidebar()
        self.sidebar.grid(column=0, row=0, sticky="nsew")

        # Initialize sections
        self.mod_updater_section = ModUpdaterSection(self)
        self.mod_generator_section = ModGeneratorSection(self)
        self.shortcuts_section = ShortcutsSection(self)
        self.settings_section = SettingsSection(self)
        self.about_section = AboutSection(self)

        # Default section
        self._set_active_section("mod_updater")



    def _set_active_section(self, section: Literal["mod_updater", "mod_generator", "settings", "about"]) -> None:
        if self.active_section == section: return

        section_frame = getattr(self, f"{section}_section", None)
        if section_frame is None: return
        section_frame.grid(column=1, row=0, sticky="nsew")
        section_frame.show()

        for key, frame in self.loaded_sections.items():
            if key != section: frame.grid_forget()

        if section_frame not in self.loaded_sections:
            self.loaded_sections[section] = section_frame

        self.active_section = section


    def configure_sidebar(self) -> None:
        def get_sidebar_logo() -> CTkImage:
            return get_ctk_image(Resources.Logo.DEFAULT, size=self._SIDEBAR_LOGO_SIZE)

        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(1, weight=1)

        # Header
        header: Frame = Frame(self.sidebar, transparent=True)
        header.grid_columnconfigure(1, weight=1)
        header.grid(column=0, row=0, sticky="nsew", padx=16, pady=16)
        logo: CTkImage = get_sidebar_logo()
        logo_label: Label = Label(header, image=logo)
        logo_label.grid(column=0, row=0, rowspan=2, padx=(0, 12), sticky="nsew")
        appname_label: Label = Label(header, key=ProjectData.NAME, style="subtitle")
        appname_label.grid(column=1, row=0, sticky="ew")
        appversion_label: Label = Label(header, key="menu.sidebar.version", modification=lambda string: Localizer.format(string, {"{app.version}": ProjectData.VERSION}), style="caption")
        appversion_label.grid(column=1, row=1, sticky="ew")

        # Main navigation
        navigation: Frame = Frame(self.sidebar, transparent=True)
        navigation.grid_columnconfigure(0, weight=1)
        navigation.grid(column=0, row=1, sticky="nsew", padx=4, pady=4)
        for i, key in enumerate(["mod_updater", "mod_generator", "shortcuts"]): Button(navigation, key=f"menu.sidebar.navigation.{key}", modification=lambda string: Localizer.format(string, {"{app.name}": ProjectData.NAME, "{roblox.common}": Localizer.Key("roblox.common"), "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"), "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")}), transparent=True, anchor="w", image=self._get_nav_icon(key), command=lambda key=key: self._set_active_section(key)).grid(column=0, row=i, sticky="ew", pady=0 if i == 0 else (4, 0))  # type: ignore

        # Footer navigation
        footer: Frame = Frame(self.sidebar, transparent=True)
        footer.grid_columnconfigure(0, weight=1)
        footer.grid(column=0, row=2, sticky="nsew", padx=4, pady=(4, 8))
        for i, key in enumerate(["settings", "about"]): Button(footer, key=f"menu.sidebar.navigation.{key}", modification=lambda string: Localizer.format(string, {"{app.name}": ProjectData.NAME, "{roblox.common}": Localizer.Key("roblox.common"), "{roblox.player}": Localizer.Key("roblox.player"), "{roblox.player_alt}": Localizer.Key("roblox.player_alt"), "{roblox.studio}": Localizer.Key("roblox.studio"), "{roblox.studio_alt}": Localizer.Key("roblox.studio_alt")}), transparent=True, anchor="w", image=self._get_nav_icon(key), command=lambda key=key: self._set_active_section(key)).grid(column=0, row=i, sticky="ew", pady=0 if i == 0 else (4, 0))  # type: ignore


    def _get_nav_icon(self, key: Literal["mod_updater", "mod_generator", "shortcuts", "settings", "about"]) -> CTkImage | None:
        try: return get_ctk_image(getattr(Resources.Navigation.Light, key.upper(), None), getattr(Resources.Navigation.Dark, key.upper(), None), self._NAV_ICON_SIZE)
        except ValueError: return None


    def _check_for_updates(self) -> None:
        try:
            Logger.info("Checking for updates...", prefix="App")
            response: Response = requests.get(Api.GitHub.LATEST_VERSION, attempts=1, cache=False, ignore_cache=True)
            data: dict = response.json()
            latest: str = data["latest"]
            current_version: Version = Version(ProjectData.VERSION)
            latest_version: Version = Version(latest)
            update_available: bool = latest_version > current_version

        except Exception as e:
            Logger.warning(f"Update check failed! {type(e).__name__}: {e}", prefix="App")

        else:
            if update_available:
                Logger.info(f"A newer version is available: {latest}", prefix="App")
                if messagebox.askyesno(
                    title=f"{ProjectData.NAME} ({ProjectData.VERSION})",
                    message=Localizer.format(Localizer.Strings["dialog.update_available.message"], {"{app.name}": ProjectData.NAME, "{latest_version}": latest})
                ):
                    Logger.info("User chose to update!", prefix="App")
                    webbrowser.open_new_tab(ProjectData.LATEST_RELEASE)
                    os._exit(os.EX_OK)