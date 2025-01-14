from typing import Optional

from modules import request
from modules.request import Api, Response
from modules.config import settings


def get(binaryType: str, channel: Optional[str] = None) -> str:
    if settings.get_value("use_live_channel"):
        channel = "LIVE"
    
    response: Response = request.get(Api.Roblox.Deployment.latest(binaryType, channel), cached=True)
    data: dict = response.json()
    return data["clientVersionUpload"]