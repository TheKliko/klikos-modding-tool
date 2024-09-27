import re
from textwrap import wrap
from typing import Literal

from modules import project_data

from . import get_size
from . import title

from ..clear import clear
from ..color import background, get_foreground, Color


class Window:
    width: int = 0
    height: int = 0
    padding_x: int = 20
    padding_y: int = 1

    data: dict = {
        "section": None,
        "description": None,
        "lines": []
    }
    project_data: dict = {}


    def __init__(self, section: str = None, description: str = None, background_color: str = None) -> None:
        
        
        self.project_data = {
            "name": project_data.NAME,
            "author": project_data.AUTHOR,
            "version": project_data.VERSION
        }
        title.set(project_data.NAME)

        self.change_section(section, description, background_color)
        self._on_update()

    def _on_update(self) -> None:
        self.width = get_size.width()
        self.height = get_size.height()

        clear()

        for i in range(self.padding_y):
            print()
        
        self._print_header()
        self._print_content()
    
    def _print_header(self) -> None:
        name = self.project_data.get("name")
        version = self.project_data.get("version")

        section = self.data.get("section")
        description = self.data.get("description")

        self._print_divider('+', '-')
        self._print_line(f"{get_foreground(Color.TITLE)}{name}")
        self._print_line(f"{get_foreground(Color.TITLE)}Version: {version}")
        self._print_divider('+', '-')

        if section is None and description is None:
            return
        
        self._print_divider()
        if section is not None:
            self._print_line(f"{get_foreground(Color.SECTION_TITLE)}{section}")
        if description is not None:
            self._print_line(f"{get_foreground(Color.SECTION_TITLE)}{description}")
        self._print_divider()
        self._print_divider('+', '-')
    
    def _print_content(self) -> None:
        lines: list[dict] = self.data["lines"]
        for item in lines:
            if item.get("is_divider", False) == True:
                self._print_divider(fill=item.get("content", '-'), border='+' if item.get("content", '-') == '-' else '|')
            else:
                self._print_line(item.get("content", ''))
    
    def _print_divider(self, border: str = '|', fill: str = ' ') -> None:
        print(f"{' '*self.padding_x}{get_foreground(Color.BORDER)}{border}{fill*(self.width-self.padding_x*2-2)}{border}{Color.RESET}")

    def _strip_ansi_codes(self, text: str) -> str:
        pattern = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return pattern.sub('', text)

    def _print_line(self, line, alignment: Literal['<', '>', '^'] = '<') -> None:
        stripped_line: str = self._strip_ansi_codes(line)
        space: int = self.width - self.padding_x * 2 - 4
        
        lines: list[str] = wrap(stripped_line, space) if len(stripped_line) > space else [line]
        for line in lines:
            stripped_line: str = self._strip_ansi_codes(line)
            padding = len(f"{stripped_line:{alignment}{space}}") - len(stripped_line)
            
            if alignment == '<':
                formatted_line = f"{line}{' ' * padding}"
            elif alignment == '>':
                formatted_line = f"{' ' * padding}{line}"
            elif alignment == '^':
                left_padding = padding // 2
                right_padding = padding - left_padding
                formatted_line = f"{' ' * left_padding}{line}{' ' * right_padding}"
            
            # textwrap.wrap loses color information :(
            print(f"{' ' * self.padding_x}{get_foreground(Color.BORDER)}|{Color.RESET} {formatted_line} {get_foreground(Color.BORDER)}|{Color.RESET}")

    def add_divider(self, fill: str = '-', count: int = 1) -> None:
        for i in range(count):
            self.add_line(fill, is_divider=True)
    
    def add_line(self, content: str, is_divider: bool = False) -> None:
        self.data["lines"].append({
            "content": content,
            "is_divider": is_divider
        })

    def remove_last(self, count: int = 1) -> None:
        for _ in range(count):
            self.data["lines"].pop()
        self._on_update()

    def remove_last_block(self, count: int = 1) -> None:
        for _ in range(count):
            lines: list[dict] = list(reversed(self.data['lines']))
            lines.pop()
            for item in lines:
                if item.get("is_divider", False) == False:
                    break
                lines.pop()
            self.data["lines"] = list(reversed(lines))
        self._on_update()

    def get_input(self, prompt: str = "", indent: int = 0) -> str:
        try:
            self._on_update()
            response: str = input(f"{' '*self.padding_x} {' '*indent}{prompt}{get_foreground(Color.INPUT)}")
            print(Color.RESET, end='')
            return response
        
        except KeyboardInterrupt:
            print(Color.RESET)
            raise

    def press_x_to_y(self, trigger: str, action: str, indent: int = 0) -> None:
        prompt: str = f"Press {get_foreground(Color.TRIGGER)}{trigger}{Color.RESET} to {get_foreground(Color.ACTION)}{action}{Color.RESET} . . ."
        self.get_input(prompt, indent)
    
    def change_section(self, section: str = None, description: str = None, background_color: str = None) -> None:
        background(background_color)
        self.data['section'] = section
        self.data['description'] = description
    
    def reset(self) -> None:
        self.data['lines'] = []
    
    def update(self) -> None:
        self._on_update()