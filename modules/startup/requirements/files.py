import sys
from pathlib import Path
import json

from modules import Logger
from modules.filesystem import File, restore_from_meipass, Directory


IS_FROZEN: bool = getattr(sys, "frozen", False)


def check_required_files() -> None:
    missing_files: list[Path] = []

    for file in File.REQUIRED_FILES:
        file_exists: bool = file.is_file()

        if file_exists:
            check_file_content(file)
        elif IS_FROZEN:
            restore_from_meipass(file)
        else:
            missing_files.append(file)

    if missing_files:
        if len(missing_files) > 1:
            raise FileNotFoundError(f"Required files not found: {','.join([file.name for file in missing_files])}")
        else:
            raise FileNotFoundError(f"Requied file not found: {file.name}")


def check_file_content(file: Path) -> None:
    if not IS_FROZEN:
        Logger.warning(f"Environment not frozen! Cannot check content of required file: {file.name}")
        return

    root: Path = Directory.ROOT
    relative_path: Path = file.relative_to(root)

    MEIPASS: Path = Path(sys._MEIPASS)
    backup: Path = MEIPASS / relative_path

    if not file.is_file():
        restore_from_meipass(file)
        return
    
    try:
        with open(file, "r") as current_file:
            current_data: dict = json.load(current_file)
        
        with open(backup, "r") as backup_file:
            backup_data: dict = json.load(backup_file)

        filtered_data: dict = backup_data.copy()
        for key in filtered_data:
            if key in current_data:
                if isinstance(current_data[key], dict):
                    if "value" in current_data[key].keys():
                        filtered_data[key]["value"] = current_data[key]["value"]

        if current_data != filtered_data:
            with open(file, "w") as current_file:
                json.dump(filtered_data, current_file, indent=4)

    except Exception as e:
        Logger.warning(f"Failed to verify content of {file.name}! {type(e).__name__}: {e}")