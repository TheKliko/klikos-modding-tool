import os
import sys
import queue
import threading
from typing import Optional

from modules.logger import logger
from modules.info import ProjectData
from modules import filesystem
from modules.filesystem import Directory
from modules.functions.restore_from_mei import restore_from_mei
from modules.functions.get_latest_version import get_latest_version
from modules.functions import mod_updater
from modules.functions.config import settings

from tkinter import messagebox
import customtkinter as ctk


IS_FROZEN = getattr(sys, "frozen", False)
hide_completion_window: bool = False

icon_path_extension: str = os.path.join("resources", "favicon.ico")
icon_path: str | None = os.path.join(Directory.root(), icon_path_extension)
if isinstance(icon_path, str):
    if not os.path.isfile(icon_path):
        if IS_FROZEN:
            restore_from_mei(icon_path)
        else:
            icon_path = None

theme_path_extension: str = os.path.join("resources", "theme.json")
theme_path: str = os.path.join(Directory.root(), theme_path_extension)
if not os.path.isfile(theme_path):
    try:
        restore_from_mei(theme_path)
    except Exception as e:
        theme_path = "blue"


class ProgressWindow(ctk.CTkToplevel):
    stop_event: threading.Event

    window_title: str = ProjectData.NAME
    window_icon: str | None = icon_path

    _has_closed: bool = False

    def __init__(self, root: ctk.CTk, mod_count: int, *args, no_root: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._no_root = no_root
        self.root = root
        self.stop_event = threading.Event()

        if self.window_icon is not None:
            self.iconbitmap(self.window_icon)
            self.after(200, lambda: self.iconbitmap(self.window_icon))
        self.title(self.window_title)

        self.protocol("WM_DELETE_WINDOW", self._set_stop_event)
        self.bind("<Escape>", lambda _: self._set_stop_event())

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.label: ctk.CTkLabel = ctk.CTkLabel(
            self,
            text=f"Updating {mod_count} mods"
        )
        self.label.grid(column=0, row=0, padx=32, pady=(32,0))

        progress_bar: ctk.CTkProgressBar = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            width=256
        )
        progress_bar.grid(column=0, row=1, padx=32, pady=(16,32))
        progress_bar.start()

        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
    
    def _set_stop_event(self) -> None:
        if not self.stop_event.is_set():
            self.stop_event.set()

    def _on_close(self) -> None:
        if self._has_closed is True:
            return
        self._set_stop_event()
        self.grab_release()
        self.destroy()
        if self._no_root:
            self.root.quit()
        self._has_closed = True

    def show(self) -> None:
        self.attributes('-topmost', True)
        self.lift()
        self.focus()
        self.grab_set()
        self.update_idletasks()
        if self._no_root:
            self.root.mainloop()
        else:
            self.wait_window()

    def close(self) -> None:
        logger.debug("Attempt to close progress window")
        self.after(0, self._on_close)


def run(mod_folder_path: str, root: Optional[ctk.CTk] = None) -> None:
    no_root: bool = False
    if root is None:
        no_root = True
        window_theme: str = theme_path
        window_appearance: str = "System"

        root = ctk.CTk()
        root.withdraw()

        ctk.set_appearance_mode(window_appearance)
        try:
            ctk.set_default_color_theme(window_theme)
        except Exception as e:
            logger.error(f"Bad theme file! {type(e).__name__}: {e}")
            logger.warning("Using default theme...")
            if IS_FROZEN:
                ctk.set_default_color_theme(os.path.join(Directory._MEI(), "resources", "theme.json"))
            else:
                ctk.set_default_color_theme("blue")
            messagebox.showwarning(ProjectData.NAME, "Bad theme file!\nReverted to default theme")

    
    mods_to_check: list[str] = [
        os.path.join(mod_folder_path, mod)
        for mod in os.listdir(mod_folder_path)
        if os.path.isfile(os.path.join(mod_folder_path, mod, "info.json"))
    ]

    logger.info(f"Updating mod: {len(mods_to_check)}...")
    exception_queue: queue.Queue = queue.Queue()

    window = ProgressWindow(root, len(mods_to_check), no_root=no_root)
    thread: threading.Thread = threading.Thread(
        name="mod-updater-main-thread_normal-mode",
        target=worker,
        args=(mods_to_check, window, exception_queue),
        daemon=True
    )
    thread.start()
    window.show()

    if not exception_queue.empty():
        error = exception_queue.get()
        raise error
    
    messagebox.showinfo(ProjectData.NAME, "Mod update complete!")
    if settings.value("open_folder_after_update"):
        filesystem.open(Directory.updated_mods())


def worker(mods_to_check: list[str], window: ProgressWindow, exception_queue: queue.Queue) -> None:
    global hide_completion_window
    try:
        if not mods_to_check:
            logger.info("No compatible mods found!")
            window.close()
            messagebox.showinfo(ProjectData.NAME, "No compatible mods found!")
            hide_completion_window = True
            return
        
        latest_version: str = get_latest_version("WindowsPlayer")
        check = mod_updater.check_for_mod_updates(mods_to_check, latest_version)
        if not check:
            logger.info("No mod updates found!")
            window.close()
            messagebox.showinfo(ProjectData.NAME, "No mod updates found!")
            hide_completion_window = True
            return
        
        mod_updater.update_mods(check, latest_version, Directory.updated_mods())
        logger.info("Finished updating mods in normal mode!")
    
    except Exception as e:
        logger.error(f"Failed to update mods in normal mode! {type(e).__name__}: {e}")
        exception_queue.put(e)

    finally:
        window.close()