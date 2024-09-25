from typing import Any
from json import load, dump

from modules.filesystem import Path


def get(setting: str) -> dict:
    for item in get_all():
        if str(item.get("name", None)).lower() != setting.lower() and item != setting:
            continue
        return item
    return {}


def get_all() -> list[dict[str,Any]]:
    with open(Path.settings(), 'r') as file:
        data: list = load(file)
    return data


def set(setting: str | dict, value: Any) -> None:
    settings: list = get_all()
    for index, item in enumerate(settings):
        if item.get("name", None) != setting and setting != item:
            continue

        if isinstance(setting, str):
            item["value"] = value
        elif isinstance(setting, dict):
            item["value"] = value
        settings.pop(index)
        settings.insert(index, item)
        break

    else:
        return
    
    with open(Path.settings(), 'w') as file:
        dump(settings, file, indent=4)