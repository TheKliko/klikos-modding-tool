from modules.api import RobloxApi
from modules import request


def get_latest_version(user_channel: str = None, binary_type: str = "WindowsPlayer") -> str:
    url: str = RobloxApi.latest_version(user_channel, binary_type)
    response = request.get(url)
    response.raise_for_status()
    data: dict = response.json()
    version: str = data["clientVersionUpload"]
    return version