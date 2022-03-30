from dataclasses import dataclass
from typing import Callable

import tcod


@dataclass
class MenuCommand:
    name: str
    command: Callable
    positional_args: list[any]
    keyword_args: dict[any, any]


class Menu:
    def __init__(self, position: tuple[int, int]):
        self.position = position
        self.menu_options: dict[str, MenuCommand] = {}
        self.curser = 0

    def curser_up(self):
        self.curser -= 1
        if self.curser < 0:
            self.curser = len(self.menu_options) - 1

    def curser_down(self):
        self.curser += 1
        if self.curser >= len(self.menu_options):
            self.curser = 0

    def add_command(self, *args, name: str, command: Callable, **kwargs):
        self.menu_options[name.upper()] = MenuCommand(name=name, command=command, positional_args=args,
                                                      keyword_args=kwargs)

    def render(self, console: tcod.Console):
        console.print(x=self.position[0], y=self.position[1], string=f" {'_' * 5}MENU{'_' * 5}")
        for item, menu_item in enumerate(self.menu_options.keys()):
            if item == self.curser:
                console.print(x=self.position[0], y=self.position[1] + item + 1, string=f'|{menu_item:<14}|',
                              fg=(0, 255, 0))
            else:
                console.print(x=self.position[0], y=self.position[1] + item + 1, string=f'|{menu_item:<14}|')
        console.print(x=self.position[0], y=self.position[1] + len(self.menu_options.keys()) + 1,
                      string=f"|{'_' * 14}|")

    @property
    def curser_key(self):
        return [key for index, key in enumerate(self.menu_options.keys()) if index == self.curser][0]

    def select(self):
        menu_command = self.menu_options[self.curser_key]
        menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
