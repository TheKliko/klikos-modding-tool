from pathlib import Path
import sys


class Directory:
    ROOT: Path = Path(__file__).parent.parent.parent if not getattr(sys, "frozen", False) else Path(sys.executable).parent
    CONFIG: Path = ROOT / "config"
    RESOURCES: Path = ROOT / "resources"
    OUTPUT_DIR: Path = ROOT / "Output"

    LOCALAPPDATA: Path = Path.home() / "AppData" / "Local"
    BLOXSTRAP_MODS_FOLDER: Path = LOCALAPPDATA / "Bloxstrap" / "Modifications"
    FISHSTRAP_MODS_FOLDER: Path = LOCALAPPDATA / "Fishstrap" / "Modifications"