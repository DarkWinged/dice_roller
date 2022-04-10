import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

import tcod
from tcod.context import Context

from color import Color
from gui_element import GuiElement


@dataclass
class MenuCommand:
    name: str
    command: Callable
    positional_args: tuple[any]
    keyword_args: dict[any, any]


class Menu(GuiElement):
    @property
    @abstractmethod
    def curser(self) -> (int, int): pass

    @curser.setter
    @abstractmethod
    def curser(self, new_curser: tuple[int, int]): pass

    @abstractmethod
    def curser_key(self): pass

    @abstractmethod
    def select(self): pass

    @abstractmethod
    def add_command(self, *args, name: str, command: Callable, **kwargs): pass

    @abstractmethod
    def process(self, fps: int, context: Context): pass

    def curser_up(self):
        self.curser = (self.curser[0], self.curser[1] - 1)
        if self.curser[1] < 0:
            self.curser = (self.curser[0], self.height - 1)

    def curser_down(self):
        self.curser = self.curser[0], self.curser[1] + 1
        if self.curser[1] >= self.height:
            self.curser = (self.curser[0], 0)

    def curser_left(self):
        self.curser = (self.curser[0] - 1, self.curser[1])
        if self.curser[0] < 0:
            self.curser = (self.width - 1, self.curser[1])

    def curser_right(self):
        self.curser = (self.curser[0] + 1, self.curser[1])
        if self.curser[0] >= self.width:
            self.curser = (0, self.curser[1])


class MovementMenu(Menu):
    def __init__(self, position: (int, int), size: (int, int), console: tcod.Console = None):
        self._position = position
        self._width = size[0]
        self._height = size[1]
        self.menu_options: dict[str, MenuCommand] = {}
        self._curser = (0, 0)
        self._activated = False
        self._paused = False
        self._console = console

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def width(self, new_height: int):
        self._height = new_height

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_width: int):
        self._width = new_width

    @property
    def canvas(self) -> tcod.Console:
        return self._console

    @canvas.setter
    def canvas(self, console: tcod.Console):
        self._console = console

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, new_position: tuple[int, int]):
        self._position = new_position

    @property
    def activated(self):
        return self._activated

    def activate(self):
        self._activated = True

    def deactivate(self):
        self._activated = False

    def curser_up(self):
        self._curser = (self._curser[0], self._curser[1] - 1)
        if self._curser[1] < 0:
            self._curser = (self._curser[0], 19)

    def curser_down(self):
        self._curser = (self._curser[0], self._curser[1] + 1)
        if self._curser[1] >= 20:
            self._curser = (self._curser[0], 0)

    def curser_left(self):
        self._curser = (self._curser[0] - 1, self._curser[1])
        if self._curser[0] < 0:
            self._curser = (19, self._curser[1])

    def curser_right(self):
        self._curser = (self._curser[0] + 1, self._curser[1])
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

    def render(self, text: str):
        if self._activated:
            x, y = self._position
            text_to_render = f'Tile Description: {text}'
            if len(text_to_render) > self._width:
                split_text = text_to_render.split(sep=' ')
                lines, line, indices = [], '', len(split_text)
                for word in split_text:
                    if len(line) + len(word) + 1 <= self._width:
                        if word == '':
                            line = f'{word}'
                        else:
                            line = f'{line} {word}'
                    else:
                        if word is not split_text[-1]:
                            lines.append(f'{line}')
                            line = ''
                        else:
                            lines.append(f'{line}')
                            lines.append(f'{word}')
                    if word is split_text[-1]:
                        lines.append(f'{line}')

                text_to_render = ''
                for line_ in lines:
                    if line_ is lines[0]:
                        text_to_render = f'{line_}'
                    else:
                        text_to_render = f'{text_to_render}\n{line_}'
            self._console.print(x=x, y=y, string=text_to_render)

    def process(self, fps: int, context: Context):
        if self._activated and not self._paused:
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
    def __init__(self, position: (int, int), size: (int, int), console: tcod.Console = None):
        self._position = position
        self._width = size[0]
        self._height = size[1]
        self.menu_options: dict[str, MenuCommand] = {}
        self._curser = (0, 0)
        self._activated = False
        self._paused = False
        self._console = console

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def width(self, new_height: int):
        self._height = new_height

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_width: int):
        self._width = new_width

    @property
    def canvas(self) -> tcod.Console:
        return self._console

    @canvas.setter
    def canvas(self, console: tcod.Console):
        self._console = console

    @property
    def activated(self):
        return self._activated

    def activate(self):
        self._activated = True

    def deactivate(self):
        self._activated = False

    def curser_up(self):
        self._curser = (self._curser[0], self._curser[1] - 1)
        if self._curser[1] < 0:
            self._curser = (self._curser[0], len(self.menu_options) - 1)

    def curser_down(self):
        self._curser = (self._curser[0], self._curser[1] + 1)
        if self._curser[1] >= len(self.menu_options):
            self._curser = (self._curser[0], 0)

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @property
    def curser(self) -> (int, int):
        return self._curser

    @curser.setter
    def curser(self, new_curser: (int, int)):
        self._curser = new_curser

    @property
    def curser_key(self):
        return [key for index, key in enumerate(self.menu_options.keys()) if index == self._curser[1]][0]

    def select(self):
        menu_command = self.menu_options[self.curser_key]
        print(f'MenuCommand{menu_command.name, menu_command.command}')
        menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)

    def add_command(self, *args, name: str, command: Callable, **kwargs):
        self.menu_options[name.upper()] = MenuCommand(name=name, command=command, positional_args=args,
                                                      keyword_args=kwargs)

    def render(self):
        if self._activated:
            height, width = self._height, self._width
            spacer = math.floor((width - 6) / 2)
            self._console.print(x=self._position[0], y=self._position[1],
                                string=f" {'_' * spacer}MENU{'_' * spacer}")
            color: Color
            for item, menu_item in enumerate(self.menu_options.keys()):
                if item == self._curser[1] and not self.paused:
                    color = Color(0.0, 1.0, 0.0)
                else:
                    color = Color(1.0, 1.0, 1.0)
                x, y = self._position
                spacer = int((width - 2 - len(menu_item)) / 2)
                self._console.print(x=x, y=y + item + 1, string=f"|{' ' * spacer}{menu_item}{' ' * spacer}|",
                                    fg=color.rgb())
            for y in range(self.height - 2 - len(self.menu_options)):
                spacer = int(width - 2)
                self._console.print(x=self._position[0], y=self._position[1] + len(self.menu_options.keys()) + 1,
                                    string=f"|{' ' * spacer}|")
            spacer = int(width - 2)
            self._console.print(x=self._position[0], y=self._position[1] + len(self.menu_options.keys()) + 1,
                                string=f"|{'_' * spacer}|")

    def process(self, fps: int, context: tcod.context.Context):
        if self._activated and not self._paused:
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
                                print(self.curser)
                            case tcod.event.K_DOWN:
                                self.curser_down()
                                print(self.curser)
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
