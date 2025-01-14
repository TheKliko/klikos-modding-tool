from pathlib import Path

from .directories import Directory


class File:
    SETTINGS: Path = Directory.CONFIG / "settings.json"

    REQUIRED_FILES: list[Path] = [
        SETTINGS
    ]