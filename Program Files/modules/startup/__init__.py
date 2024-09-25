from modules import interface

from . import dependencies
from .check_core_files import check_core_files


def run() -> None:
    check_core_files()
    dependencies.check()
    # idk what else to add here