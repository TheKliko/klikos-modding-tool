from typing import Literal

from modules.request import RobloxApi, Response
from modules import request
from modules.functions.config import settings


def get_user_channel(binary_type: Literal["WindowsPlayer", "WindowsStudio"]) -> str:
    forced_channel: str | None = settings.value("user_channel")
    if forced_channel is not None:
        return forced_channel
    
    response: Response = request.get(RobloxApi.user_channel(binary_type), cache=True)
    data: dict = response.json()
    return data["channelName"]