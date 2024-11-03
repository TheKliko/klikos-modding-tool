import os
import sys

from modules.logger import logger
from modules import error_handler, launch_mode

IS_FROZEN = getattr(sys, "frozen", False)
if IS_FROZEN:
    import pyi_splash
else:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libraries"))

from modules import startup, menu, bloxstrap_mode


def main():
    try:
        startup.run()

        mode: str = launch_mode.get()
        logger.info(f"Launch mode: {mode}")

        if mode.lower() == "menu":
            window = menu.MainWindow()
        elif mode.lower() == "bloxstrap":
            if IS_FROZEN:
                if pyi_splash.is_alive():
                    pyi_splash.close()
            bloxstrap_mode.run()

        else:
            raise Exception(f"Unknown launch mode: {mode}")

        if mode.lower() == "menu":
            if IS_FROZEN:
                if pyi_splash.is_alive():
                    pyi_splash.close()
            
            window.show()


    except Exception as e:
        error_handler.run(e)


    finally:
        logger.info("Shuting down...")


if __name__ == "__main__":
    main()