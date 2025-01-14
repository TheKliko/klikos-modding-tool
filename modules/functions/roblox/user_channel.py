from modules import request
from modules.request import Api, Response
from modules.config import settings


def get(binaryType: str) -> str:
    if settings.get_value("use_live_channel"):
        return "LIVE"

    response: Response = request.get(Api.Roblox.Deployment.channel(binaryType), cached=True)
    data: dict = response.json()
    return data["channelName"]