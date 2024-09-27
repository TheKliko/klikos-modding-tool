from modules.api import RobloxApi
from modules import request


def get_user_channel() -> str | None:
    try:
        url: str = RobloxApi.user_channel()
        response =  request.get(url)
        response.raise_for_status()
        data: dict = response.json()
        channel: str = data.get("channelName", None)
        return channel

    except:
        return None