from os import path
from sys import version_info


class Path:
    @staticmethod
    def root() -> str:
        return path.dirname(path.dirname(path.dirname(path.dirname(__file__))))
    
    @staticmethod
    def program_files() -> str:
        return path.dirname(path.dirname(path.dirname(__file__)))
    
    @staticmethod
    def libraries() -> str:
        return path.join(Path.program_files(), "libraries")
    
    @staticmethod
    def version_specific_libraries() -> str:
        python_version: str = f"{version_info.major}.{version_info.minor}"
        return path.join(Path.program_files(), "version_specific_libraries", f"python-{python_version}")
    
    @staticmethod
    def settings() -> str:
        return path.join(Path.program_files(), "config", "settings.json")
    
    @staticmethod
    def mod_generator() -> str:
        return path.join(Path.program_files(), "config", "mod_generator.json")