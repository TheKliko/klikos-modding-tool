import sys
from pathlib import Path

from modules import Logger  # Imported first to initialize the logger
from modules import exception_handler


ROOT: Path = Path(__file__).parent
LIBRARIES_PATH: Path = Path(ROOT, "libraries")


def main() -> None:
    try:
        if getattr(sys, "frozen", False):
            try:
                import pyi_splash
                if pyi_splash.is_alive():
                    pyi_splash.close()
            except (ModuleNotFoundError, ImportError):
                pass
        else:
            sys.path.insert(0, str(LIBRARIES_PATH))


        from modules import startup
        startup.run()

        from modules import menu
        menu.run()


    except Exception as e:
        exception_handler.run(e)
    
    finally:
        Logger.info("Shutting down...")


if __name__ == "__main__":
    main()