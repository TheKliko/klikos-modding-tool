from tkinter import TclError, StringVar, BooleanVar
from typing import Optional, Literal, TYPE_CHECKING

from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, DropDownMenu, ToggleSwitch
from modules.localization import Localizer
from modules.interfaces.config import ConfigInterface

if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import set_appearance_mode  # type: ignore


class SettingsSection(ScrollableFrame):
    loaded: bool = False
    root: "Root"
    appearance_mode_variable: StringVar
    _language_change_callback_id: str | None = None

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8

    _ENTRY_GAP: int = 8
    _ENTRY_PADDING: tuple[int, int] = (16, 16)
    _ENTRY_INNER_GAP: int = 8


    def __init__(self, master):
        super().__init__(master, transparent=False, round=True, border=True, layer=1)
        self.root = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def destroy(self):
        if self._language_change_callback_id is not None:
            Localizer.remove_callback(self._language_change_callback_id)
            self._language_change_callback_id = None
        return super().destroy()


    def clear(self) -> None:
        if self._language_change_callback_id is not None:
            Localizer.remove_callback(self._language_change_callback_id)
            self._language_change_callback_id = None
        for widget in self.winfo_children():
            try: widget.destroy()
            except TclError: pass
        self.loaded = False


    def refresh(self) -> None:
        self.clear()
        self.show()


    def show(self) -> None:
        self.load()


# region load
    def load(self) -> None:
        if self.loaded: return

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_PADX, pady=self._SECTION_PADY)

        self._load_header(content)
        self._load_content(content)

        if self._language_change_callback_id is not None:
            Localizer.remove_callback(self._language_change_callback_id)
            self._language_change_callback_id = None
        self._language_change_callback_id = Localizer.add_callback(self._on_language_change)

        self.loaded = True


    def _load_header(self, master) -> None:
        header: Frame = Frame(master, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        Label(header, "menu.settings.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.settings.header.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")


    def _load_content(self, master) -> None:
        wrapper: Frame = Frame(master, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)
        wrapper.grid(column=0, row=1, sticky="nsew")
        row_counter: int = -1

        # Appearance mode
        row_counter += 1
        frame: Frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.settings.content.appearance.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], self._ENTRY_INNER_GAP), padx=self._ENTRY_PADDING[0])
        appearance_mode_option_keys: list[str] = ["menu.settings.content.appearance.light", "menu.settings.content.appearance.dark", "menu.settings.content.appearance.system"]
        appearance_mode: Literal["light", "dark", "system"] = ConfigInterface.get_appearance_mode()
        appearance_mode_value: str = Localizer.format(Localizer.Strings[appearance_mode_option_keys[0 if appearance_mode == "light" else 1 if appearance_mode == "dark" else 2]], {"{appearance.light}": Localizer.Key("appearance.light"), "{appearance.dark}": Localizer.Key("appearance.dark"), "{appearance.system}": Localizer.Key("appearance.system")})
        self.appearance_mode_variable = StringVar(value=appearance_mode_value)
        DropDownMenu(frame, appearance_mode_option_keys, [
                lambda string: Localizer.format(string, {"{appearance.light}": Localizer.Key("appearance.light")}),
                lambda string: Localizer.format(string, {"{appearance.dark}": Localizer.Key("appearance.dark")}),
                lambda string: Localizer.format(string, {"{appearance.system}": Localizer.Key("appearance.system")})
            ], variable = self.appearance_mode_variable, command=self._update_appearance_mode
        ).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=self._ENTRY_PADDING[0])


        # Update checker
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.settings.content.check_for_updates.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.settings.content.check_for_updates.description", lambda string: Localizer.format(string, {"{app.name}": ProjectData.NAME}), style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value = ConfigInterface.get("check_for_updates")
        switch_var = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("check_for_updates", var.get(), "menu.settings.content.check_for_updates.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))


        # Open folder after update
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.settings.content.open_dir_after_update.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.settings.content.open_dir_after_update.description", lambda string: Localizer.format(string, {"{app.name}": ProjectData.NAME}), style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value = ConfigInterface.get("open_dir_after_update")
        switch_var = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("open_dir_after_update", var.get(), "menu.settings.content.open_dir_after_update.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))


        # Open folder after generate
        row_counter += 1
        frame = Frame(wrapper, layer=2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=row_counter, sticky="nsew", pady=0 if row_counter == 0 else (self._ENTRY_GAP, 0))
        Label(frame, "menu.settings.content.open_dir_after_generate.title", style="body_strong", autowrap=True).grid(column=0, row=0, sticky="sew", pady=(self._ENTRY_PADDING[1], 0), padx=(self._ENTRY_PADDING[0], 0))
        Label(frame, "menu.settings.content.open_dir_after_generate.description", lambda string: Localizer.format(string, {"{app.name}": ProjectData.NAME}), style="caption", autowrap=True).grid(column=0, row=1, sticky="new", pady=(0, self._ENTRY_PADDING[1]), padx=(self._ENTRY_PADDING[0], 0))
        value = ConfigInterface.get("open_dir_after_generate")
        switch_var = BooleanVar(value=value)
        ToggleSwitch(frame, variable=switch_var, command=lambda var=switch_var: self._update_boolean_setting("open_dir_after_generate", var.get(), "menu.settings.content.open_dir_after_generate.title")).grid(column=1, row=0, rowspan=2, sticky="e", pady=self._ENTRY_PADDING[1], padx=(self._ENTRY_INNER_GAP, self._ENTRY_PADDING[0]))
# endregion


# region functions
    def _on_language_change(self) -> None:
        if not self.loaded:
            self.after(100, self._on_language_change)
            return

        appearance_mode_option_keys: list[str] = ["menu.settings.content.appearance.light", "menu.settings.content.appearance.dark", "menu.settings.content.appearance.system"]
        appearance_mode: Literal["light", "dark", "system"] = ConfigInterface.get_appearance_mode()
        appearance_mode_value: str = Localizer.format(Localizer.Strings[appearance_mode_option_keys[0 if appearance_mode == "light" else 1 if appearance_mode == "dark" else 2]], {"{appearance.light}": Localizer.Key("appearance.light"), "{appearance.dark}": Localizer.Key("appearance.dark"), "{appearance.system}": Localizer.Key("appearance.system")})
        self.appearance_mode_variable.set(appearance_mode_value)


    def _update_appearance_mode(self, value: str) -> None:
        light_value: str = Localizer.format(Localizer.Strings["menu.settings.content.appearance.light"], {"{appearance.light}": Localizer.Key("appearance.light")})
        dark_value: str = Localizer.format(Localizer.Strings["menu.settings.content.appearance.dark"], {"{appearance.dark}": Localizer.Key("appearance.dark")})
        system_value: str = Localizer.format(Localizer.Strings["menu.settings.content.appearance.system"], {"{appearance.system}": Localizer.Key("appearance.system")})

        if value not in {light_value, dark_value, system_value}:
            self.root.send_banner(
                title_key="menu.settings.exception.title.failed_to_update",
                title_modification=lambda string: Localizer.format(string, {"{setting.name}": Localizer.Key("menu.settings.content.appearance.title")}),
                message_key="menu.settings.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": "ValueError", "{exception.message}": f'Bad value: "{value}". Expected one of "{light_value}", "{dark_value}", "{system_value}"'}),
                mode="error", auto_close_after_ms=6000
            )
            return

        normalized_value: Literal["light", "dark", "system"] = "light" if value == light_value else "dark" if value == dark_value else "system"
        try:
            ConfigInterface.set_appearance_mode(normalized_value)
            set_appearance_mode(normalized_value)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.settings.exception.title.failed_to_update",
                title_modification=lambda string: Localizer.format(string, {"{setting.name}": Localizer.Key("menu.settings.content.appearance.title")}),
                message_key="menu.settings.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )


    def _update_boolean_setting(self, key: str, value: bool, localizer_name_key: Optional[str] = None) -> None:
        if not localizer_name_key: name: str = key
        else:
            name = Localizer.Strings[localizer_name_key]

        try: ConfigInterface.set(key, value)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.settings.exception.title",
                title_modification=lambda string: Localizer.format(string, {"{setting.name}": Localizer.Key(name)}),
                message_key="menu.settings.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
# endregion