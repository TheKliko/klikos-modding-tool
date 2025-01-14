from typing import Literal
from pathlib import Path

from modules import request
from modules.request import Api, Response
from modules.filesystem.directories import Directory
from modules.functions.roblox import user_channel


class Deployment:
    channel: str
    version: str
    git_hash: str
    file_version: str

    binaryType: str
    executable_name: str


    def __init__(self, mode: Literal["Player", "Studio"]):
        self.binaryType = f"WindowsStudio64" if mode == "Studio" else f"WindowsPlayer"
        self.executable_name = f"Roblox{mode}Beta.exe"

        self.channel = user_channel.get(self.binaryType)
        self.version, self.git_hash = self._get_version_info(self.binaryType, self.channel)


    def _get_version_info(self, binaryType: str, channel: str) -> tuple[str,str]:
        if channel is None:
            channel = user_channel.get(binaryType)
        response: Response = request.get(Api.Roblox.Deployment.latest(binaryType, channel), cached=True)
        data: dict = response.json()
        return (data["clientVersionUpload"], data["version"])