from typing import Optional
import time

from modules import Logger

import requests
from requests import Response, ConnectionError


COOLDOWN: float = 2
TIMEOUT: tuple[int,int] = (5,15)
_cache: dict = {}


# region APIs
class Api:
    class GitHub:
        LATEST_VERSION: str = r"https://raw.githubusercontent.com/TheKliko/klikos-modding-tool/refs/heads/main/GitHub%20Files/version.json"
        RELEASE_INFO: str = r"https://api.github.com/repos/thekliko/klikos-modding-tool/releases/latest"
        MOD_GENERATOR_BLACKLIST: str = r"https://raw.githubusercontent.com/TheKliko/klikos-modloader/refs/heads/config/mod_generator_blacklist.json"
        MARKETPLACE: str = r"https://raw.githubusercontent.com/TheKliko/klikos-modloader/refs/heads/remote-mod-downloads/index.json"
        @staticmethod
        def mod_thumbnail(id: str) -> str:
            return rf"https://raw.githubusercontent.com/TheKliko/klikos-modloader/refs/heads/remote-mod-downloads/thumbnails/{id}.png"
        @staticmethod
        def mod_download(id: str) -> str:
            return rf"https://raw.githubusercontent.com/TheKliko/klikos-modloader/refs/heads/remote-mod-downloads/mods/{id}.zip"
    
    class Roblox:
        FASTFLAGS: str = r"https://clientsettingscdn.roblox.com/v2/settings/application/PCDesktopClient"

        class Deployment:
            HISTORY: str = r"https://setup.rbxcdn.com/DeployHistory.txt"
            @staticmethod
            def channel(binaryType: str) -> str:
                return rf"https://clientsettings.roblox.com/v2/user-channel?binaryType={binaryType}"
            @staticmethod
            def latest(binaryType: str, channel: Optional[str] = None) -> str:
                if channel is None:
                    rf"https://clientsettingscdn.roblox.com/v2/client-version/{binaryType}"
                return rf"https://clientsettingscdn.roblox.com/v2/client-version/{binaryType}/channel/{channel}"
            @staticmethod
            def manifest(version: str) -> str:
                return rf"https://setup.rbxcdn.com/{version}-rbxPkgManifest.txt"
            @staticmethod
            def download(version: str, file: str) -> str:
                return rf"https://setup.rbxcdn.com/{version}-{file}"


# region get()
def get(url: str, attempts: int = 3, cached: bool = False, timeout: Optional[tuple[int, int]] = None, dont_log_cached_request: bool = False) -> Response:
    if cached and url in _cache:
        if not dont_log_cached_request:
            Logger.info(f"Cached GET request: {url}")
        return _cache[url]
    
    exception: Exception | None = None

    for _ in range(attempts):
        try:
            Logger.info(f"GET request: {url}")
            response: Response = requests.get(url, timeout=timeout or TIMEOUT)
            response.raise_for_status()
            _cache[url] = response
            return response

        except Exception as e:
            Logger.error(f"GET request failed! {type(e).__name__}: {e}")
            exception = e
            time.sleep(COOLDOWN)
    
    if exception is not None:
        raise exception