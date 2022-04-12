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
    def __init__(self):
        self._curser = (0, 0)
        self._position = (0, 0)
        self._console = None
        self._width = 0
        self._height = 0
        self._activated = False
        self._paused = True
        self._key_codes = {'ESCAPE': tcod.event.K_ESCAPE}

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_height: int):
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
    def curser(self) -> tuple[int, int]:
        return self._curser

    @curser.setter
    def curser(self, new_curser: tuple[int, int]):
        self._curser = new_curser

    @property
    def key_codes(self) -> dict[str, tcod.event_constants]:
        return self._key_codes

    @key_codes.setter
    def key_codes(self, new_key_codes: dict[str, tcod.event_constants]):
        self._key_codes = new_key_codes

    def add_command(self, *args, name: str, command: Callable, **kwargs):
        self.menu_options[name.upper()] = MenuCommand(
            name=name,
            command=command,
            positional_args=args,
            keyword_args=kwargs
        )

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    @property
    def activated(self):
        return self._activated

    def activate(self):
        self._activated = True

    def deactivate(self):
        self._activated = False

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

    @abstractmethod
    def process(self, fps: int, context: Context): pass


class MovementMenu(Menu):

    def __init__(self, position: tuple[int, int], size: tuple[int, int], console: tcod.Console = None):
        self._position = position
        self._width = size[0]
        self._height = size[1]
        self.menu_options: dict[str, MenuCommand] = {}
        self._curser = (0, 0)
        self._activated = False
        self._paused = False
        self._console = console
        self._key_codes = {
            'UP': tcod.event.K_UP,
            'DOWN': tcod.event.K_DOWN,
            'LEFT': tcod.event.K_LEFT,
            'RIGHT': tcod.event.K_RIGHT
        }

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

    def _text_wrap(self, text_to_wrap: str) -> str:
        split_text = text_to_wrap.split(sep=' ')
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

        text_to_wrap = ''
        for line_ in lines:
            if line_ is lines[0]:
                text_to_wrap = f'{line_}'
            else:
                text_to_wrap = f'{text_to_wrap}\n{line_}'
        return text_to_wrap

    def render(self, text: str):
        if self._activated:
            x, y = self._position
            text = f'Tile Description: {text}'
            if len(text) > self._width:
                text = self._text_wrap(text)
            self._console.print(x=x, y=y, string=text)

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
                        if event.sym == self._key_codes['UP']:
                            self.curser_up()
                        elif event.sym == self._key_codes['DOWN']:
                            self.curser_down()
                        elif event.sym == self._key_codes['LEFT']:
                            self.curser_left()
                        elif event.sym == self._key_codes['RIGHT']:
                            self.curser_right()
                        elif event.sym == tcod.event.K_RETURN:
                            menu_command = self.menu_options['confirm'.upper()]
                            print(f'MenuCommand{menu_command.name, menu_command.command}')
                            menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
                        elif event.sym == tcod.event.K_ESCAPE:
                            menu_command = self.menu_options['cancel'.upper()]
                            print(f'MenuCommand{menu_command.name, menu_command.command}')
                            menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)


class ListedMenu(Menu):
    def __init__(self, position: tuple[int, int], size: tuple[int, int], console: tcod.Console = None):
        self._position = position
        self._width = size[0]
        self._height = size[1]
        self.menu_options: dict[str, MenuCommand] = {}
        self._curser = (0, 0)
        self._activated = False
        self._paused = False
        self._console = console
        self._key_codes = {
            'UP': tcod.event.K_UP,
            'DOWN': tcod.event.K_DOWN
        }
        self._hidden: list[str] = []
        self._overrides: dict[tcod.event_constants, str] = {}

    def curser_up(self):
        self._curser = (self._curser[0], self._curser[1] - 1)
        if self._curser[1] < 0:
            self._curser = (self._curser[0], len(self.menu_options) - 1)
        while self.curser_key in self._hidden and len(self.menu_options) > len(self._hidden):
            self.curser_up()

    def curser_down(self):
        self._curser = (self._curser[0], self._curser[1] + 1)
        if self._curser[1] >= len(self.menu_options):
            self._curser = (self._curser[0], 0)
        while self.curser_key in self._hidden and len(self.menu_options) > len(self._hidden):
            self.curser_down()

    @property
    def curser(self) -> tuple[int, int]:
        return self._curser

    @curser.setter
    def curser(self, new_curser: tuple[int, int]):
        self._curser = new_curser
        while self.curser_key in self._hidden and len(self.menu_options) > len(self._hidden):
            self.curser_up()

    @property
    def curser_key(self):
        return [key for index, key in enumerate(self.menu_options.keys()) if index == self._curser[1]][0]

    def select(self):
        menu_command = self.menu_options[self.curser_key]
        print(f'MenuCommand{menu_command.name, menu_command.command}')
        menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)

    def add_command(self, *args, name: str, command: Callable, hidden: bool = None,
                    override: tcod.event_constants = None, **kwargs):
        if override is not None:
            if override in self._overrides.keys():
                override_error = ValueError(f'override({override}: {name.upper()}) already exists as override({override}: {self._overrides[override]})')
                raise override_error
            self._overrides[override] = name.upper()
        self.menu_options[name.upper()] = MenuCommand(
            name=name,
            command=command,
            positional_args=args,
            keyword_args=kwargs
        )
        if hidden:
            self._hidden.append(name.upper())
        while self.curser_key in self._hidden and len(self.menu_options) > len(self._hidden):
            self.curser_up()

    def render(self):
        if self._activated:
            skipped = 0
            height, width = self._height, self._width
            color: Color = Color(1.0, 1.0, 1.0)
            spacer = math.floor((width - 6) / 2)
            self._console.print(
                x=self._position[0],
                y=self._position[1],
                string=f" {'_' * spacer}MENU{'_' * spacer}",
                fg=color.rgb(),
            )
            for item, menu_item in enumerate(self.menu_options.keys()):
                if menu_item in self._hidden:
                    spacer = int((width - 2) / 2)
                    self._console.print(
                        x=self._position[0],
                        y=self._position[1] + item + 1 - skipped,
                        string=f"|{' ' * spacer}|"
                    )
                    skipped += 1
                else:
                    if item == self._curser[1] and not self.paused:
                        color = Color(0.0, 1.0, 0.0)
                    else:
                        color = Color(1.0, 1.0, 1.0)
                    x, y = self._position
                    spacer = int((width - 2 - len(menu_item)) / 2)
                    if len(menu_item) % 2 == 1:
                        self._console.print(
                            x=x,
                            y=y + item + 1 - skipped,
                            string=f"|{' ' * spacer}{menu_item}{' ' * (spacer+ 1 )}|",
                            fg=color.rgb())

                    else:
                        self._console.print(
                            x=x,
                            y=y + item + 1 - skipped,
                            string=f"|{' ' * spacer}{menu_item}{' ' * spacer}|",
                            fg=color.rgb()
                        )
            color = Color(1.0, 1.0, 1.0)
            for y in range(self.height - 2 - len(self.menu_options)):
                spacer = int(width - 2)
                self._console.print(
                    x=self._position[0],
                    y=self._position[1] + len(self.menu_options.keys()) + 1 - skipped,
                    string=f"|{' ' * spacer}|",
                    fg=color.rgb()
                )
            spacer = int(width - 2)
            self._console.print(
                x=self._position[0],
                y=self._position[1] + len(self.menu_options.keys()) + 1 - skipped,
                string=f"|{'_' * spacer}|"
            )

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
                        if event.sym in self._overrides:
                            name = self._overrides[event.sym]
                            menu_command = self.menu_options[name]
                            print(f'MenuCommand{menu_command.name, menu_command.command}')
                            menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
                        else:
                            if event.sym == self._key_codes['UP']:
                                self.curser_up()
                            elif event.sym == self._key_codes['DOWN']:
                                self.curser_down()
                            elif event.sym == tcod.event.K_RETURN:
                                print(
                                    self.menu_options[self.curser_key].name,
                                    self.menu_options[self.curser_key].command
                                )
                                self.select()
                            elif event.sym == tcod.event.K_ESCAPE:
                                menu_command = self.menu_options['quit'.upper()]
                                print(f'MenuCommand{menu_command.name, menu_command.command}')
                                menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)


class TextMenu(Menu):
    char_codes = {
        tcod.event.K_a: 'A',
        tcod.event.K_b: 'C',
        tcod.event.K_d: 'D',
        tcod.event.K_e: 'E',
        tcod.event.K_f: 'F',
        tcod.event.K_g: 'G',
        tcod.event.K_h: 'H',
        tcod.event.K_i: 'I',
        tcod.event.K_j: 'J',
        tcod.event.K_k: 'K',
        tcod.event.K_l: 'L',
        tcod.event.K_m: 'M',
        tcod.event.K_n: 'N',
        tcod.event.K_o: 'O',
        tcod.event.K_p: 'P',
        tcod.event.K_q: 'Q',
        tcod.event.K_r: 'R',
        tcod.event.K_s: 'S',
        tcod.event.K_t: 'T',
        tcod.event.K_u: 'U',
        tcod.event.K_v: 'V',
        tcod.event.K_w: 'W',
        tcod.event.K_x: 'X',
        tcod.event.K_y: 'Y',
        tcod.event.K_z: 'Z',
    }

    def __init__(self, position: tuple[int, int], size: tuple[int, int], console: tcod.Console = None):
        self._position = position
        self._width = size[0]
        self._height = size[1]
        self.menu_options: dict[str, MenuCommand] = {}
        self._curser = (0, 0)
        self._activated = False
        self._paused = False
        self._console = console
        self._key_codes = {
            'LEFT': tcod.event.K_LEFT,
            'RIGHT': tcod.event.K_RIGHT
        }
        self._text = ''
        self._text_field = ''

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text

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
                        if event.sym == self._key_codes['LEFT']:
                            self.curser_left()
                        elif event.sym == self._key_codes['RIGHT']:
                            self.curser_right()
                        elif event.sym in self.char_codes.keys():
                            self._text_field = f'{self._text_field}{self.char_codes[event.sym]}'
                        elif event.sym == tcod.event.K_BACKSPACE:
                            new_text_field = ''
                            for char in range(len(self._text_field)-1):
                                new_text_field = f'{new_text_field}{self._text_field[char]}'
                            self._text_field = new_text_field
                        elif event.sym == tcod.event.K_RETURN:
                            menu_command = self.menu_options['confirm'.upper()]
                            print(f'MenuCommand{menu_command.name, menu_command.command}')
                            menu_command.command(self._text_field, *menu_command.positional_args, **menu_command.keyword_args)
                        elif event.sym == tcod.event.K_ESCAPE:
                            menu_command = self.menu_options['cancel'.upper()]
                            print(f'MenuCommand{menu_command.name, menu_command.command}')
                            menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)

    def render(self):
        if self._activated:
            x, y = self._position
            text = f'{self._text}\n{self._text_field}'
            """
            if len(text) > self._width:
                text = self._text_wrap(text)
            """
            self._console.print(x=x, y=y, string=text)
