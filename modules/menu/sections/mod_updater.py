from pathlib import Path
from tkinter import messagebox
from threading import Thread
from typing import Literal
from tkinter import filedialog
from tempfile import TemporaryDirectory
import shutil

from modules import Logger
from modules.info import ProjectData
from modules import filesystem
from modules.filesystem import Directory, restore_from_meipass
from modules.functions.interface.image import load as load_image
from modules.config import settings
from modules.launcher.deployment_info import Deployment
from modules.mod_updater import check_for_mod_updates, update_mods

import customtkinter as ctk


class ModUpdaterSection:
    class Constants:
        SECTION_TITLE: str = "Mod Updater"
        SECTION_DISCLAIMER: str = "Update compatible mods"
        ENTRY_INNER_PADDING: int = 8
        ENTRY_OUTER_PADDING: int = 12
        ENTRY_GAP: int = 8

    class Fonts:
        title: ctk.CTkFont
        large: ctk.CTkFont
        bold: ctk.CTkFont


    root: ctk.CTk
    container: ctk.CTkScrollableFrame
    progress_variable: ctk.StringVar
    is_running: bool = False
    selected_directory_var: ctk.StringVar
    selected_directory: Path | None = None


    def __init__(self, root: ctk.CTk, container: ctk.CTkScrollableFrame) -> None:
        self.root = root
        self.container = container

        self.Fonts.title = ctk.CTkFont(size=20, weight="bold")
        self.Fonts.large = ctk.CTkFont(size=16)
        self.Fonts.bold = ctk.CTkFont(weight="bold")
        
        self.selected_directory_var = ctk.StringVar()
        self.progress_variable = ctk.StringVar()


    def show(self) -> None:
        self._destroy()
        self._load_title()
        self._load_content()


    def _destroy(self) -> None:
        for widget in self.container.winfo_children():
            widget.destroy()


    # region title
    def _load_title(self) -> None:
        frame: ctk.CTkFrame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid(column=0, row=0, sticky="nsew", pady=(0,16))

        ctk.CTkLabel(frame, text=self.Constants.SECTION_TITLE, anchor="w", font=self.Fonts.title).grid(column=0, row=0, sticky="nsew")
        ctk.CTkLabel(frame, text=self.Constants.SECTION_DISCLAIMER, anchor="w", font=self.Fonts.large).grid(column=0, row=1, sticky="nsew")
    # endregion


    # region content
    def _load_content(self) -> None:
        container: ctk.CTkFrame = ctk.CTkFrame(self.container, fg_color="transparent")
        container.grid_columnconfigure(0, weight=1)
        container.grid(column=0, row=1, sticky="nsew", padx=(0,4))
        
        run_icon: Path = (Directory.RESOURCES / "menu" / "common" / "run").with_suffix(".png")
        if not run_icon.is_file():
            restore_from_meipass(run_icon)
        run_image = load_image(run_icon)

        file_select_icon: Path = (Directory.RESOURCES / "menu" / "common" / "file-select").with_suffix(".png")
        if not file_select_icon.is_file():
            restore_from_meipass(file_select_icon)
        file_select_image = load_image(file_select_icon)
        
        # region normal mode
        single_mode_frame: ctk.CTkFrame = ctk.CTkFrame(container)
        single_mode_frame.grid(column=0, row=0, sticky="nsw")

        single_mode_title_frame: ctk.CTkFrame = ctk.CTkFrame(single_mode_frame, fg_color="transparent")
        single_mode_title_frame.grid(column=0, row=0, sticky="nsew", padx=self.Constants.ENTRY_OUTER_PADDING, pady=(self.Constants.ENTRY_OUTER_PADDING, 0))
        ctk.CTkLabel(single_mode_title_frame, text="Normal mode", anchor="w", font=self.Fonts.bold).grid(column=0, row=0)
        
        content_frame: ctk.CTkFrame = ctk.CTkFrame(single_mode_frame, fg_color="transparent")
        content_frame.grid(column=0, row=1, sticky="nsew", padx=self.Constants.ENTRY_OUTER_PADDING, pady=(0, self.Constants.ENTRY_OUTER_PADDING))

        ctk.CTkEntry(content_frame, textvariable=self.selected_directory_var, state="disabled", width=258, height=40).grid(column=0, row=0, sticky="nw")
        ctk.CTkButton(content_frame, image=file_select_image, command=self._select_directory, text="", width=40, height=40).grid(column=1, row=0, sticky="nw", padx=(4,0))

        buttons_frame: ctk.CTkFrame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.grid(column=0, row=1, sticky="nw", columnspan=2, pady=(self.Constants.ENTRY_INNER_PADDING, 0))

        ctk.CTkButton(buttons_frame, text="Run single mode", image=run_image, command=lambda: self._run(self.selected_directory, batch_mode=False), width=1, anchor="w", compound=ctk.LEFT).grid(column=0, row=0, sticky="w")
        # Batch mode is temporarily disabled because it's not detecting all outdated mods
        # ctk.CTkButton(buttons_frame, text="Run batch mode", image=run_image, command=lambda: self._run(self.selected_directory, batch_mode=True), width=1, anchor="w", compound=ctk.LEFT).grid(column=1, row=0, sticky="w", padx=(4,0))

        # region bloxstrap mode
        if (Directory.BLOXSTRAP_MODS_FOLDER / "info.json").is_file():
            bloxstrap_mode_frame: ctk.CTkFrame = ctk.CTkFrame(container)
            bloxstrap_mode_frame.grid(column=0, row=3, sticky="nsw", pady=(self.Constants.ENTRY_GAP, 0))

            bloxstrap_mode_title_frame: ctk.CTkFrame = ctk.CTkFrame(bloxstrap_mode_frame, fg_color="transparent")
            bloxstrap_mode_title_frame.grid(column=0, row=0, sticky="nsew", padx=self.Constants.ENTRY_OUTER_PADDING, pady=(self.Constants.ENTRY_OUTER_PADDING, 0))
            ctk.CTkLabel(bloxstrap_mode_title_frame, text="Bloxstrap mode", anchor="w", font=self.Fonts.bold).grid(column=0, row=0)
        
            bloxstrap_mode_content_frame: ctk.CTkFrame = ctk.CTkFrame(bloxstrap_mode_frame, fg_color="transparent")
            bloxstrap_mode_content_frame.grid(column=0, row=1, sticky="nsew", padx=self.Constants.ENTRY_OUTER_PADDING, pady=(0, self.Constants.ENTRY_OUTER_PADDING))

            ctk.CTkButton(bloxstrap_mode_content_frame, text="Run Bloxstrap mode", image=run_image, command=lambda: self._run(Directory.BLOXSTRAP_MODS_FOLDER, batch_mode=False), width=1, anchor="w", compound=ctk.LEFT).grid(column=0, row=0, sticky="w", pady=(self.Constants.ENTRY_INNER_PADDING, 0))

        # region fishstrap mode
        if (Directory.FISHSTRAP_MODS_FOLDER / "info.json").is_file():
            fishstrap_mode_frame: ctk.CTkFrame = ctk.CTkFrame(container)
            fishstrap_mode_frame.grid(column=0, row=4, sticky="nsw", pady=(self.Constants.ENTRY_GAP, 0))

            fishstrap_mode_title_frame: ctk.CTkFrame = ctk.CTkFrame(fishstrap_mode_frame, fg_color="transparent")
            fishstrap_mode_title_frame.grid(column=0, row=0, sticky="nsew", padx=self.Constants.ENTRY_OUTER_PADDING, pady=(self.Constants.ENTRY_OUTER_PADDING, 0))
            ctk.CTkLabel(fishstrap_mode_title_frame, text="Fishstrap mode", anchor="w", font=self.Fonts.bold).grid(column=0, row=0)
        
            fishstrap_mode_content_frame: ctk.CTkFrame = ctk.CTkFrame(fishstrap_mode_frame, fg_color="transparent")
            fishstrap_mode_content_frame.grid(column=0, row=1, sticky="nsew", padx=self.Constants.ENTRY_OUTER_PADDING, pady=(0, self.Constants.ENTRY_OUTER_PADDING))

            ctk.CTkButton(fishstrap_mode_content_frame, text="Run Fishstrap mode", image=run_image, command=lambda: self._run(Directory.FISHSTRAP_MODS_FOLDER, batch_mode=False), width=1, anchor="w", compound=ctk.LEFT).grid(column=0, row=0, sticky="w", pady=(self.Constants.ENTRY_INNER_PADDING, 0))

        # Progress label
        ctk.CTkLabel(container, textvariable=self.progress_variable, anchor="w", font=self.Fonts.bold).grid(column=0, row=4, sticky="w", pady=(4, 0))

    # endregion


    # region functions
    def _select_directory(self) -> None:
        initial_dir: Path = Path.home()
        if (initial_dir / "Downloads").is_dir():
            initial_dir = initial_dir / "Downloads"

        directory: str | Literal[''] = filedialog.askdirectory(
            title=f"{ProjectData.NAME} | Choose a mod", initialdir=initial_dir,
        )

        if directory == '':
            return
        
        path: Path = Path(directory)
        self.selected_directory_var.set(path.name)
        self.selected_directory = path

    
    def _run(self, path: Path | None, batch_mode: bool = False) -> None:
        Thread(name="mod-updater-thread", target=self._actually_run, kwargs={"path":path,"batch_mode":batch_mode}, daemon=True).start()


    def _actually_run(self, path: Path | None, batch_mode: bool = False) -> None:
        if self.is_running:
            return
        
        if path is None:
            return
        
        if batch_mode:
            compatible_mods: list[Path] = [directory for directory in path.iterdir() if directory.is_dir() and (directory / "info.json").is_file()]

        if not batch_mode and not (path / "info.json").is_file():
            messagebox.showerror(ProjectData.NAME, "Incompatible mod!")
            return
        
        if batch_mode and not compatible_mods:
            messagebox.showerror(ProjectData.NAME, "No compatible mods found!")
            return
        
        existing_mods: list[str] = [mod.name for mod in Directory.OUTPUT_DIR.iterdir()]

        if not batch_mode:
            if path.name in existing_mods:
                if not messagebox.askokcancel(ProjectData.NAME, "Anther mod with the same name already exists in the output directory!\nDo you wish to overwrite it?"):
                    return
        else:
            for directory_name in [directory.name for directory in compatible_mods]:
                if directory_name in existing_mods:
                    if not messagebox.askokcancel(ProjectData.NAME, f"Anther mod with the name '{directory_name}' already exists in the output directory!\nDo you wish to overwrite it?"):
                        return

        self.is_running = True
        self.root.after(0, self.progress_variable.set, "Updating... please wait")
        try:
            deployment: Deployment = Deployment("Player")
            Logger.info(f"The current Roblox version is {deployment.version}")

            with TemporaryDirectory(prefix="klikos-modding-tool_mod-updater_") as tmp:
                temporary_directory: Path = Path(tmp)
                
                if not batch_mode:
                    shutil.copytree(path, temporary_directory / path.name)
                
                else:
                    for item in compatible_mods:
                        shutil.copytree(item, temporary_directory / item.name)
                
                mods_to_check: list[str] = [item.name for item in temporary_directory.iterdir()]
                Logger.info(f"Checking for mod updates: {', '.join(mods_to_check)}")
                check: dict[str, list[Path]] | Literal[False] = check_for_mod_updates(temporary_directory, mods_to_check, deployment.version)
                if not check:
                    messagebox.showerror(ProjectData.NAME, "No outdated mod(s) found!")
                    return
                
                print(check)
                update_mods(check, deployment.version, Directory.OUTPUT_DIR)
                messagebox.showinfo(ProjectData.NAME, "Mod(s) updated successfully!")
                if settings.get_value("open_folder_after_mod_update"):
                    filesystem.open(Directory.OUTPUT_DIR)

        except Exception as e:
            messagebox.showerror(ProjectData.NAME, message=f"Error while updating mod(s)! {type(e).__name__}: {e}")
        
        self.is_running = False
        self.root.after(0, self.progress_variable.set, "")
    # endregion