from tkinter import TclError, filedialog
import shutil
from pathlib import Path
from threading import Thread
from typing import Literal, TYPE_CHECKING

from modules.project_data import ProjectData
from modules.frontend.widgets import ScrollableFrame, Frame, Label, Button, FlexBox
from modules.frontend.functions import get_ctk_image
from modules.localization import Localizer
from modules.filesystem import Resources, Directories
from modules.mod_updater import ModUpdater
from modules.interfaces.config import ConfigInterface
from modules.deployments import LatestVersion
from modules import filesystem
from modules.logger import Logger
if TYPE_CHECKING: from modules.frontend.widgets import Root

from customtkinter import CTkImage  # type: ignore


class ModUpdaterSection(ScrollableFrame):
    _LOG_PREFIX: str = "ModUpdaterSection"
    loaded: bool = False
    root: "Root"

    updating: bool = False
    _update_buttons: list[Button]

    _SECTION_PADX: int | tuple[int, int] = (8, 4)
    _SECTION_PADY: int | tuple[int, int] = 8
    _BACKGROUND_TASK_INTERVAL: int = 50
    _ENTRY_GAP: int = 8
    _ENTRY_PADDING: tuple[int , int] = (12, 12)
    _ENTRY_INNER_GAP: int = 4
    _ENTRY_SIZE: tuple[int, int] = (320, (_ENTRY_INNER_GAP+2*_ENTRY_PADDING[1]+28+32))


    def __init__(self, master):
        super().__init__(master, transparent=False, round=True, border=True, layer=1)
        self.root = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def destroy(self):
        return super().destroy()


    def clear(self) -> None:
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
        self._update_buttons = []

        content: Frame = Frame(self, transparent=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid(column=0, row=0, sticky="nsew", padx=self._SECTION_PADX, pady=self._SECTION_PADY)

        self._load_header(content)
        self._load_content(content)

        self.loaded = True


    def _load_header(self, master) -> None:
        header: Frame = Frame(master, transparent=True)
        header.grid_columnconfigure(0, weight=1)
        header.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        Label(header, "menu.mod_updater.header.title", style="title", autowrap=True).grid(column=0, row=0, sticky="ew")
        Label(header, "menu.mod_updater.header.description", style="caption", autowrap=True).grid(column=0, row=1, sticky="ew")


    def _load_content(self, master) -> None:
        wrapper: FlexBox = FlexBox(master, column_width=self._ENTRY_SIZE[0], row_height=self._ENTRY_SIZE[1], gap=self._ENTRY_GAP, transparent=True, layer=1)
        wrapper.grid(column=0, row=1, sticky="nsew")

        normal_frame: Frame = wrapper.add_item()
        self._create_normal_frame(normal_frame)

        if Directories.BLOXSTRAP_MOD.is_dir():
            bloxstrap_frame: Frame = wrapper.add_item()
            self._create_bloxstrap_frame(bloxstrap_frame)

        if Directories.FISHSTRAP_MOD.is_dir():
            fishstrap_frame: Frame = wrapper.add_item()
            self._create_fishstrap_frame(fishstrap_frame)
# endregion


# region functions
    def _create_normal_frame(self, frame: Frame) -> None:
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        wrapper: Frame = Frame(frame, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

        Label(wrapper, "menu.mod_updater.content.normal_mode", style="body_strong", autowrap=False).grid(column=0, row=0, sticky="ew")
        image: CTkImage = get_ctk_image(Resources.Common.Light.START, Resources.Common.Dark.START, 24)
        button: Button = Button(wrapper, "menu.mod_updater.content.button.update", secondary=True, image=image, command=self.select_mod_to_update)
        button.grid(column=0, row=1, sticky="ew", pady=self._ENTRY_INNER_GAP)
        self._update_buttons.append(button)


    def _create_bloxstrap_frame(self, frame: Frame) -> None:
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        wrapper: Frame = Frame(frame, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

        Label(wrapper, "menu.mod_updater.content.bloxstrap_mode", style="body_strong", autowrap=False).grid(column=0, row=0, sticky="ew")
        image: CTkImage = get_ctk_image(Resources.Common.Light.START, Resources.Common.Dark.START, 24)
        button: Button = Button(wrapper, "menu.mod_updater.content.button.update", secondary=True, image=image, command=lambda:Thread(target=lambda:self.update_mod(Directories.BLOXSTRAP_MOD, "bloxstrap"), daemon=True).start())
        button.grid(column=0, row=1, sticky="ew", pady=self._ENTRY_INNER_GAP)
        self._update_buttons.append(button)


    def _create_fishstrap_frame(self, frame: Frame) -> None:
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        wrapper: Frame = Frame(frame, transparent=True)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid(column=0, row=0, sticky="nsew", padx=self._ENTRY_PADDING[0], pady=self._ENTRY_PADDING[1])

        Label(wrapper, "menu.mod_updater.content.fishstrap_mode", style="body_strong", autowrap=False).grid(column=0, row=0, sticky="ew")
        image: CTkImage = get_ctk_image(Resources.Common.Light.START, Resources.Common.Dark.START, 24)
        button: Button = Button(wrapper, "menu.mod_updater.content.button.update", secondary=True, image=image, command=lambda:Thread(target=lambda:self.update_mod(Directories.FISHSTRAP_MOD, "fishstrap"), daemon=True).start())
        button.grid(column=0, row=1, sticky="ew", pady=self._ENTRY_INNER_GAP)
        self._update_buttons.append(button)
# endregion


# region update
    def select_mod_to_update(self) -> None:
        if self.updating:
            self.root.send_banner(
                title_key="menu.mod_updater.exception.title.update",
                message_key="menu.mod_updater.exception.message.generator_busy",
                mode="warning", auto_close_after_ms=6000
            )
            return

        directory: str | Literal[""] = filedialog.askdirectory(
            initialdir=str(Directories.DOWNLOADS),
            title=Localizer.format(Localizer.Strings["menu.mod_updater.filedialog.title"], {"{app.name}": ProjectData.NAME})
        )

        if directory:
            Thread(target=lambda: self.update_mod(Path(directory).resolve(), "normal"), daemon=True).start()  # type: ignore


    def update_mod(self, path: Path, mode: Literal["normal", "bloxstrap", "fishstrap"]) -> None:
        Logger.info("Running mod updater...", prefix=self._LOG_PREFIX)
        if self.updating:
            self.root.send_banner(
                title_key="menu.mod_updater.exception.title.update",
                message_key="menu.mod_updater.exception.message.generator_busy",
                mode="warning", auto_close_after_ms=6000
            )
            return

        if mode == "normal" and path is None:
            self.root.send_banner(
                title_key="menu.mod_updater.exception.title.update",
                message_key="menu.mod_updater.exception.message.no_mod_selected",
                mode="warning", auto_close_after_ms=6000
            )
            return

        self.updating = True
        for button in self._update_buttons:
            button.configure(key="menu.mod_updater.content.button.updating")

        try:
            latest_version: LatestVersion = LatestVersion("WindowsStudio64")
            is_outdated: bool = ModUpdater.check_for_updates(path, latest_version)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.mod_updater.exception.title.update",
                message_key="menu.mod_updater.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
            self.updating = False
            return

        if not is_outdated:
            self.root.send_banner(
                title_key="menu.mod_updater.exception.title.update",
                message_key="menu.mod_updater.exception.message.not_outdated",
                mode="warning", auto_close_after_ms=6000
            )
            self.updating = False
            return

        try:
            if mode == "normal":
                output_path: Path = Directories.OUTPUT_DIR_UPDATER / path.name
                if output_path.exists():
                    shutil.rmtree(output_path)
                output_path.mkdir(parents=True, exist_ok=True)
                shutil.copytree(path, output_path, dirs_exist_ok=True)
                path = output_path

        except Exception as e:
            self.root.send_banner(
                title_key="menu.mod_updater.exception.title.unknown",
                message_key="menu.mod_updater.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )
            self.updating = False
            return

        try:
            ModUpdater.update_mod(path, latest_version)

        except Exception as e:
            self.root.send_banner(
                title_key="menu.mod_updater.exception.title.update",
                message_key="menu.mod_updater.exception.message.unknown",
                message_modification=lambda string: Localizer.format(string, {"{exception.type}": f"{type(e).__module__}.{type(e).__qualname__}", "{exception.message}": str(e)}),
                mode="error", auto_close_after_ms=6000
            )

        else:
            match mode:
                case "normal":
                    self.root.send_banner(
                        title_key="menu.mod_updater.success.title.update",
                        message_key="menu.mod_updater.success.message.update",
                        message_modification=lambda string: Localizer.format(string, {"{mod.name}": path.name}),
                        mode="success", auto_close_after_ms=4000
                    )
                    if ConfigInterface.get("open_dir_after_update"):
                        filesystem.open(Directories.OUTPUT_DIR_UPDATER)
                case "bloxstrap":
                    self.root.send_banner(
                        title_key="menu.mod_updater.success.title.update",
                        message_key="menu.mod_updater.success.message.update_bloxstrap",
                        mode="success", auto_close_after_ms=4000
                    )
                case "fishstrap":
                    self.root.send_banner(
                        title_key="menu.mod_updater.success.title.update",
                        message_key="menu.mod_updater.success.message.update_fishstrap",
                        mode="success", auto_close_after_ms=4000
                    )

        self.updating = False
        for button in self._update_buttons:
            button.configure(key="menu.mod_updater.content.button.update")
# endregion