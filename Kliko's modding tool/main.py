"""
Kliko's modding tool: A python tool made for Roblox mod developers 
Source: https://github.com/thekliko/klikos-modding tool
License: MIT
"""

import sys
import platform
from pathlib import Path


FROZEN: bool = getattr(sys, "frozen", False)
if FROZEN:
    try:
        import pyi_splash  # type: ignore
        if pyi_splash.is_alive(): pyi_splash.close()
    except (ImportError, ModuleNotFoundError): pass
else:
    print("[WARNING] You are running the source code directly, please make sure you have all dependencies installed or run the build script.")

ROOT: Path = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT / "libraries"))


try:
    from modules.logger import Logger
    from modules.project_data import ProjectData
    from modules.localization import Localizer
    from modules.interfaces.config import ConfigInterface
    from modules.filesystem import Directories
    from modules import exception_handler
except (ImportError, ModuleNotFoundError) as e:
    print(f"[CRITICAL] Missing requires libraries!\n{type(e).__name__}: {e}")
    input("\nPress enter to exit")
    sys.exit(1)


def log_debug_info() -> None:
    if not FROZEN: Logger.warning("Environment not frozen!")
    Logger.debug(f"{ProjectData.NAME} v{ProjectData.VERSION}")
    Logger.debug(f"Platform: {platform.system()} {platform.release()}")


def initialize_localization() -> None:
    Logger.info("Initializing localization...")
    Localizer.initialize()
    Localizer.set_language(Localizer.Metadata.DEFAULT_LANGUAGE)


def main() -> None:
    Logger.initialize()
    ConfigInterface.verify_file_integrity()
    log_debug_info()
    initialize_localization()

    try:
        from modules.frontend import menu
        menu.run()

    except Exception as e: exception_handler.run(e)
    Logger.info("Shutting down...")


if __name__ == "__main__":
    main()