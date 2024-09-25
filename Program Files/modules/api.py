class RobloxApi:
    @staticmethod
    def user_channel(binary_type: str = "WindowsPlayer") -> str:
        return rf'https://clientsettings.roblox.com/v2/user-channel?binaryType={binary_type}'

    @staticmethod
    def latest_version(user_channel: str = None, binary_type: str = "WindowsPlayer") -> str:
        if user_channel is None:
            return rf'https://clientsettingscdn.roblox.com/v2/client-version/{binary_type}'
        return rf'https://clientsettingscdn.roblox.com/v2/client-version/{binary_type}/channel/{user_channel}'
    
    @staticmethod
    def package_manifest(version: str) -> str:
        return rf'https://setup.rbxcdn.com/{version}-rbxPkgManifest.txt'
    
    @staticmethod
    def download(version: str, file: str) -> str:
        return rf'https://setup.rbxcdn.com/{version}-{file}'
    
    @staticmethod
    def deploy_history() -> str:
        return r'https://setup.rbxcdn.com/DeployHistory.txt'