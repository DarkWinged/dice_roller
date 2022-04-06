from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

import tcod
from tcod.context import Context

from color import Color


@dataclass
class MenuCommand:
    name: str
    command: Callable
    positional_args: tuple[any]
    keyword_args: dict[any, any]


class Menu(ABC):
    @abstractmethod
    def activate(self): pass
    @abstractmethod
    def deactivate(self): pass
    @abstractmethod
    def activated(self): pass
    @property
    @abstractmethod
    def curser(self): pass
    @curser.setter
    @abstractmethod
    def curser(self, new_curser: tuple[int, int]): pass
    @property
    @abstractmethod
    def position(self): pass
    @position.setter
    @abstractmethod
    def position(self, new_curser: tuple[int, int]): pass
    @abstractmethod
    def curser_key(self): pass
    @abstractmethod
    def select(self): pass
    @abstractmethod
    def add_command(self, *args, name: str, command: Callable, **kwargs): pass
    @abstractmethod
    def render(self, console: tcod.Console): pass
    @abstractmethod
    def process(self, fps: int, context: Context): pass


class MovementMenu(Menu):
    def __init__(self, position: tuple[int, int]):
        self._position = position
        self.menu_options: dict[str, MenuCommand] = {}
        self._curser = (0, 0)
        self._activated = False

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    def activate(self):
        self._activated = True

    def deactivate(self):
        self._activated = False

    @property
    def activated(self):
        return self._activated

    def curser_up(self):
        self._curser = (self._curser[0], self._curser[1]-1)
        if self._curser[1] < 0:
            self._curser = (self._curser[0], 19)

    def curser_down(self):
        self._curser = (self._curser[0], self._curser[1]+1)
        if self._curser[1] >= 20:
            self._curser = (self._curser[0], 0)

    def curser_left(self):
        self._curser = (self._curser[0]-1, self._curser[1])
        if self._curser[0] < 0:
            self._curser = (19, self._curser[1])

    def curser_right(self):
        self._curser = (self._curser[0]+1, self._curser[1])
        if self._curser[0] >= 20:
            self._curser = (0, self._curser[1])

    @property
    def curser(self):
        return self._curser

    @curser.setter
    def curser(self, new_curser: tuple[int, int]):
        self._curser = new_curser

    @property
    def curser_key(self):
        return [key for index, key in enumerate(self.menu_options.keys()) if index == self._curser[1]][0]

    def select(self):
        pass

    def add_command(self, *args, name: str, command: Callable, **kwargs):
        self.menu_options[name.upper()] = MenuCommand(name=name, command=command, positional_args=args,
                                                      keyword_args=kwargs)

    def render(self, console: tcod.Console):
        pass

    def process(self, fps: int, context: Context):
        if self._activated:
            for event in tcod.event.wait(1.0 / fps):
                context.convert_event(event)
                match event:
                    case tcod.event.Quit():
                        print(f"KeyDown: {event}")
                        menu_command = self.menu_options['quit'.upper()]
                        print(f'MenuCommand{menu_command.name, menu_command.command}')
                        menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
                    case tcod.event.KeyDown():
                        print(f"KeyDown: {event}")
                        match event.sym:
                            case tcod.event.K_UP:
                                self.curser_up()
                            case tcod.event.K_DOWN:
                                self.curser_down()
                            case tcod.event.K_LEFT:
                                self.curser_left()
                            case tcod.event.K_RIGHT:
                                self.curser_right()
                            case tcod.event.K_RETURN:
                                menu_command = self.menu_options['confirm'.upper()]
                                print(f'MenuCommand{menu_command.name, menu_command.command}')
                                menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
                            case tcod.event.K_ESCAPE:
                                menu_command = self.menu_options['cancel'.upper()]
                                print(f'MenuCommand{menu_command.name, menu_command.command}')
                                menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)


class MainMenu(Menu):
    def __init__(self, position: tuple[int, int]):
        self._position = position
        self.menu_options: dict[str, MenuCommand] = {}
        self._curser = 0
        self._activated = False

    def activate(self):
        self._activated = True

    def deactivate(self):
        self._activated = False

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @property
    def activated(self):
        return self._activated

    def curser_up(self):
        self._curser -= 1
        if self._curser < 0:
            self._curser = len(self.menu_options) - 1

    def curser_down(self):
        self._curser += 1
        if self._curser >= len(self.menu_options):
            self._curser = 0

    @property
    def curser(self):
        return -1, self._curser

    @property
    def curser_key(self):
        return [key for index, key in enumerate(self.menu_options.keys()) if index == self._curser][0]

    def select(self):
        menu_command = self.menu_options[self.curser_key]
        print(f'MenuCommand{menu_command.name, menu_command.command}')
        menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)

    def add_command(self, *args, name: str, command: Callable, **kwargs):
        self.menu_options[name.upper()] = MenuCommand(name=name, command=command, positional_args=args,
                                                      keyword_args=kwargs)

    def render(self, console: tcod.Console):
        if self._activated:
            console.print(x=self._position[0], y=self._position[1], string=f" {'_' * 5}MENU{'_' * 5}")
            color: Color
            for item, menu_item in enumerate(self.menu_options.keys()):
                if item == self._curser:
                    color = Color(0.0, 1.0, 0.0)
                else:
                    color = Color(1.0, 1.0, 1.0)
                x, y = self._position
                console.print(x=x, y=y + item + 1, string=f'|{menu_item:<14}|', fg=color.rgb())
            console.print(x=self._position[0], y=self._position[1] + len(self.menu_options.keys()) + 1,
                          string=f"|{'_' * 14}|")

    def process(self, fps: int, context: Context):
        if self._activated:
            for event in tcod.event.wait(1.0 / fps):
                context.convert_event(event)
                match event:
                    case tcod.event.Quit():
                        print(f"KeyDown: {event}")
                        menu_command = self.menu_options['quit'.upper()]
                        print(f'MenuCommand{menu_command.name, menu_command.command}')
                        menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
                    case tcod.event.KeyDown():
                        print(f"KeyDown: {event}")
                        match event.sym:
                            case tcod.event.K_UP:
                                self.curser_up()
                            case tcod.event.K_DOWN:
                                self.curser_down()
                            case tcod.event.K_RETURN:
                                print(
                                    self.menu_options[self.curser_key].name,
                                    self.menu_options[self.curser_key].command
                                    )
                                self.select()
                            case tcod.event.K_ESCAPE:
                                menu_command = self.menu_options['quit'.upper()]
                                print(f'MenuCommand{menu_command.name, menu_command.command}')
                                menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
                """
                    case tcod.event.MouseButtonDown():
                        print(f"MouseButtonDown: {event}")
                    case tcod.event.MouseMotion():
                        print(f"MouseMotion: {event}")
                    case tcod.event.Event() as event:
                        print(event)
                """
