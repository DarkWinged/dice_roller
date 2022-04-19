import math

import tcod

from gui_element import GuiElement
from map_token import CreatureToken


class StatusTab(GuiElement):

    def __init__(self, position: tuple[int, int], size: tuple[int, int], console: tcod.Console = None):
        self._paused = False
        self._activated = False
        self._height = size[1]
        self._width = size[0]
        self._position = position
        self._console = console
        self._token = None

    @property
    def activated(self) -> bool:
        return self._activated

    def activate(self):
        self._activated = True

    def deactivate(self):
        self._activated = False

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, new_position: tuple[int, int]):
        self._position = new_position

    @property
    def token(self) -> CreatureToken:
        return self._token

    @token.setter
    def token(self, new_token: CreatureToken):
        self._token = new_token

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
    def canvas(self, new_console: tcod.Console):
        return self._console

    def render(self):
        text_to_print = ''

        text_to_print = f"{text_to_print}\n{self.center_text(f'{self.token.name}')}"
        text_to_print = f'{text_to_print}\n{self.render_health_bar()}'

        x, y = self._position
        self._console.print(x=x, y=y, string=text_to_print)

    def render_health_bar(self) -> str:
        max_hp = self._token.sheet.max_hp
        hp = self._token.sheet.hp
        health_bar = ''
        health_bar = f"{health_bar}{self.center_text('HEALTH')}\n{self.center_text(f'({hp}/{max_hp})')}\n"
        health_bar = f"{health_bar}["
        health_bar = f"{health_bar}{'=' * (math.ceil((hp / max_hp) * (self._width-2)))}"
        health_bar = f"{health_bar}{' ' * math.floor((1 - (hp / max_hp)) * (self._width-2))}"
        health_bar = f"{health_bar}]"
        return health_bar

    def center_text(self, text: str) -> str:
        shift_amount = int((self._width - len(text))/2)
        return f"{' ' * shift_amount}{text}"
