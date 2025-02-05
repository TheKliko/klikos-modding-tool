from pathlib import Path
import re
from tkinter import messagebox
from threading import Thread
import webbrowser

from modules.info import ProjectData
from modules import filesystem
from modules.filesystem import Directory, restore_from_meipass
from modules.functions.interface.image import load as load_image, load_from_image
from modules.config import settings
from modules import mod_generator
from modules.mod_generator.get_mask import get_mask

import customtkinter as ctk
from PIL import Image, ImageColor


class ModGeneratorSection:
    class Constants:
        SECTION_TITLE: str = "Mod Generator [BETA]"
        SECTION_DISCLAIMER: str = "Disclaimer: this tool only generates the ImageSets, it does not generate a complete mod"
        PREVIEW_SIZE: int = 64
    
    class Fonts:
        title: ctk.CTkFont
        large: ctk.CTkFont
        bold: ctk.CTkFont


    root: ctk.CTk
    container: ctk.CTkScrollableFrame
    mod_name_entry: ctk.CTkEntry
    color1_entry: ctk.CTkEntry
    color2_entry: ctk.CTkEntry
    angle_entry: ctk.CTkEntry
    preview_image: ctk.CTkLabel
    default_image: Image.Image
    progress_variable: ctk.StringVar
    is_running: bool = False


    def __init__(self, root: ctk.CTk, container: ctk.CTkScrollableFrame) -> None:
        self.root = root
        self.container = container
        self.Fonts.title = ctk.CTkFont(size=20, weight="bold")
        self.Fonts.large = ctk.CTkFont(size=16)
        self.Fonts.bold = ctk.CTkFont(weight="bold")
        
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

        # name input
        name_frame: ctk.CTkFrame = ctk.CTkFrame(container, fg_color="transparent")
        name_frame.grid(column=0, row=0, sticky="nsew")
        ctk.CTkLabel(name_frame, text="Mod name", anchor="w", font=self.Fonts.bold).grid(column=0, row=0, sticky="nw")
        self.mod_name_entry = ctk.CTkEntry(
            name_frame, width=256, height=40, validate="key",
            validatecommand=(self.root.register(lambda value: not re.search(r'[\\/:*?"<>|]', value)), "%P")
        )
        self.mod_name_entry.grid(column=0, row=1, sticky="nw")
        
        # color/angle inputs
        color_frame: ctk.CTkFrame = ctk.CTkFrame(container, fg_color="transparent")
        color_frame.grid(column=0, row=1, sticky="nsew", pady=(16, 0))

        color1_frame: ctk.CTkFrame = ctk.CTkFrame(color_frame, fg_color="transparent")
        color1_frame.grid(column=0, row=1)
        ctk.CTkLabel(color1_frame, text="Color 1 (required)", anchor="w", font=self.Fonts.bold).grid(column=0, row=0, sticky="w")
        self.color1_entry = ctk.CTkEntry(color1_frame, width=150, height=40)
        self.color1_entry.grid(column=0, row=1, sticky="w")
        self.color1_entry.bind("<Return>", lambda _: self.root.focus())
        self.color1_entry.bind("<Control-s>", lambda _: self.root.focus())
        self.color1_entry.bind("<FocusOut>", lambda _: self._generate_preview())

        color2_frame: ctk.CTkFrame = ctk.CTkFrame(color_frame, fg_color="transparent")
        color2_frame.grid(column=1, row=1, padx=12)
        ctk.CTkLabel(color2_frame, text="Color 2 (optional)", anchor="w", font=self.Fonts.bold).grid(column=0, row=0, sticky="w")
        self.color2_entry = ctk.CTkEntry(color2_frame, width=150, height=40)
        self.color2_entry.grid(column=0, row=1, sticky="w")
        self.color2_entry.bind("<Return>", lambda _: self.root.focus())
        self.color2_entry.bind("<Control-s>", lambda _: self.root.focus())
        self.color2_entry.bind("<FocusOut>", lambda _: self._generate_preview())

        angle_frame: ctk.CTkFrame = ctk.CTkFrame(color_frame, fg_color="transparent")
        angle_frame.grid(column=2, row=1)
        ctk.CTkLabel(angle_frame, text="Angle (optional)", anchor="w", font=self.Fonts.bold).grid(column=0, row=0, sticky="w")
        self.angle_entry = ctk.CTkEntry(
            angle_frame, width=120, height=40, validate="key",
            validatecommand=(self.root.register(lambda value: value.removeprefix("-").isdigit() or value == ""), "%P")
        )
        self.angle_entry.grid(column=0, row=1, sticky="w")
        self.angle_entry.bind("<Return>", lambda _: self.root.focus())
        self.angle_entry.bind("<Control-s>", lambda _: self.root.focus())
        self.angle_entry.bind("<FocusOut>", lambda _: self._generate_preview())

        possible_colors_frame: ctk.CTkFrame = ctk.CTkFrame(container, fg_color="transparent")
        possible_colors_frame.grid(column=0, row=2, sticky="w", pady=(4, 0))
        ctk.CTkLabel(possible_colors_frame, text="A list of available color formats can be found at ").grid(column=0, row=0)
        url: str = r"https://pillow.readthedocs.io/en/stable/reference/ImageColor.html#color-names"
        unhover_color: str | tuple[str ,str] = ("#0000EE", "#2fa8ff")
        hover_color: str | tuple[str ,str] = ("#0000CC", "#58bbff")
        hyperlink: ctk.CTkLabel = ctk.CTkLabel(possible_colors_frame, text=url, cursor="hand2", text_color=unhover_color)
        hyperlink.bind("<Button-1>", lambda _: self._open_in_browser(url))
        hyperlink.grid(column=1, row=0)
        hyperlink.bind("<Enter>", lambda _: hyperlink.configure(text_color=hover_color))
        hyperlink.bind("<Leave>", lambda _: hyperlink.configure(text_color=unhover_color))

        # Preview
        preview_frame: ctk.CTkFrame = ctk.CTkFrame(container, fg_color="transparent")
        preview_frame.grid(column=0, row=3, sticky="nsew", pady=(16, 0))

        ctk.CTkLabel(preview_frame, text="Preview", anchor="w", font=self.Fonts.bold).grid(column=0, row=0, sticky="w")
        self.preview_image = ctk.CTkLabel(preview_frame, text="", fg_color="#000", width=self.Constants.PREVIEW_SIZE, height=self.Constants.PREVIEW_SIZE)
        self.preview_image.grid(column=0, row=1, sticky="w")
        self._generate_preview(default=True)

        # region TODO
        # TODO: let user select additional files

        # Buttons
        buttons_frame: ctk.CTkFrame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.grid(column=0, row=4, sticky="nsew", pady=(32, 0))

        run_icon: Path = (Directory.RESOURCES / "menu" / "common" / "image-run").with_suffix(".png")
        if not run_icon.is_file():
            restore_from_meipass(run_icon)
        run_image = load_image(run_icon)
        
        ctk.CTkButton(buttons_frame, text="Generate mod", image=run_image, command=self._run, width=1, anchor="w", compound=ctk.LEFT).grid(column=0, row=0, sticky="w")
        
        # Progress label
        ctk.CTkLabel(container, textvariable=self.progress_variable, anchor="w", font=self.Fonts.bold).grid(column=0, row=5, sticky="w", pady=(4, 0))

    # endregion


    # region functions
    def _open_in_browser(self, url: str) -> None:
        webbrowser.open_new_tab(url)

    
    def _generate_preview(self, default: bool = False) -> None:
        if default:
            self.default_image: Image.Image = get_mask(ImageColor.getcolor("black", "RGBA"), None, 0, size=(self.Constants.PREVIEW_SIZE, self.Constants.PREVIEW_SIZE))
            self.preview_image.configure(image=load_from_image(self.default_image, identifier=f"mod_generator_default_preview", size=(self.Constants.PREVIEW_SIZE, self.Constants.PREVIEW_SIZE)))
            return

        color1: str = self.color1_entry.get()
        color2: str = self.color2_entry.get()
        angle: str | int = self.angle_entry.get()

        if not color1 or color1 == "None":
            self.preview_image.configure(image=load_from_image(self.default_image, identifier=f"mod_generator_default_preview", size=(self.Constants.PREVIEW_SIZE, self.Constants.PREVIEW_SIZE)))
            return
        
        else:
            try:
                rgba_color1 = ImageColor.getcolor(color1, "RGBA")
            except Exception:
                try:
                    rgba_color1 = ImageColor.getcolor(f"#{color1}", "RGBA")
                except Exception:
                    self.preview_image.configure(image=load_from_image(self.default_image, identifier=f"mod_generator_default_preview", size=(self.Constants.PREVIEW_SIZE, self.Constants.PREVIEW_SIZE)))
                    return
        
        if color2:
            try:
                rgba_color2 = ImageColor.getcolor(color2, "RGBA")
            except Exception:
                try:
                    rgba_color2 = ImageColor.getcolor(f"#{color2}", "RGBA")
                except Exception:
                    self.preview_image.configure(image=load_from_image(self.default_image, identifier=f"mod_generator_default_preview", size=(self.Constants.PREVIEW_SIZE, self.Constants.PREVIEW_SIZE)))
                    return
        else:
            rgba_color2 = None
        
        if not angle or angle == "None" or angle == "-":
            angle = 0
        
        try:
            angle = int(angle)
        except Exception as e:
            messagebox.showerror(ProjectData.NAME, f"Bad angle input!\n{type(e).__name__}: {e}")
            return

        image: Image.Image = get_mask(rgba_color1, rgba_color2, angle, size=(self.Constants.PREVIEW_SIZE, self.Constants.PREVIEW_SIZE))
        self.preview_image.configure(image=load_from_image(image, identifier=f"{rgba_color1}-{rgba_color2}-{angle}", size=(self.Constants.PREVIEW_SIZE, self.Constants.PREVIEW_SIZE)))


    def _run(self) -> None:
        Thread(name="mod-generator-thread", target=self._actually_run, daemon=True).start()


    def _actually_run(self) -> None:
        name: str = self.mod_name_entry.get()
        color1: str = self.color1_entry.get()
        color2: str = self.color2_entry.get()
        angle: str | int = self.angle_entry.get()

        if self.is_running:
            return

        if not name:
            messagebox.showwarning(ProjectData.NAME, "Enter a name first!")
            return

        if name in [mod.name for mod in Directory.OUTPUT_DIR.iterdir()]:
            messagebox.showerror(ProjectData.NAME, "Anther mod with the same name already exists in the output directory!")
            return

        if not color1 or color1 == "None":
            messagebox.showwarning(ProjectData.NAME, "Choose a color!")
            return
        
        else:
            try:
                rgba_color1 = ImageColor.getcolor(color1, "RGBA")
            except Exception as e:
                try:
                    rgba_color1 = ImageColor.getcolor(f"#{color1}", "RGBA")
                except Exception:
                    messagebox.showwarning(ProjectData.NAME, f"Bad color 1 input!\n{type(e).__name__}: {e}")
                    return
        
        if color2:
            try:
                rgba_color2 = ImageColor.getcolor(color2, "RGBA")
            except Exception as e:
                try:
                    rgba_color2 = ImageColor.getcolor(f"#{color2}", "RGBA")
                except Exception:
                    messagebox.showwarning(ProjectData.NAME, f"Bad color 2 input!\n{type(e).__name__}: {e}")
                    return
        else:
            rgba_color2 = None
        
        if not angle or angle == "None" or angle == "-":
            angle = 0
        
        try:
            angle = int(angle)
        except Exception as e:
            messagebox.showerror(ProjectData.NAME, f"Bad angle input!\n{type(e).__name__}: {e}")
            return

        self.is_running = True
        self.root.after(0, self.progress_variable.set, "Generating... please wait")
        
        try:
            mod_generator.run(name, rgba_color1, rgba_color2, angle, output_dir=Directory.OUTPUT_DIR)
            messagebox.showinfo(ProjectData.NAME, "Mod generated successfully!")
            if settings.get_value("open_folder_after_mod_generate"):
                filesystem.open(Directory.OUTPUT_DIR)
        
        except Exception as e:
            messagebox.showerror(ProjectData.NAME, message=f"Error while generating mod! {type(e).__name__}: {e}")
        
        self.is_running = False
        self.root.after(0, self.progress_variable.set, "")
    # endregion