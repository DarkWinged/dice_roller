import tcod

from gui_element import GuiElement
from map_token import CreatureToken
from character_sheet.enums import AbilityScore
from menus import Menu


def fetch_game_data(key: str, data: any, layer: int) -> str:
    if isinstance(key, AbilityScore):
        as_key: AbilityScore = key
        key = as_key.name
    if isinstance(data, int):
        return f"{' ' * layer}{key}: {data}"
    elif isinstance(data, str):
        return f"{' ' * layer}{key}: {data}"
    elif isinstance(data, float):
        return f"{' ' * layer}{key}: {data:2f}"
    elif isinstance(data, tuple):
        result = f"{' ' * layer}{key}: (\n"
        for index, item in enumerate(data):
            result = f"{result}{fetch_game_data(str(index), item, int(layer + 1))}\n"
        return f"{result}{' ' * layer})"
    elif isinstance(data, list):
        result = f"{' ' * layer}{key}: [\n"
        for index, item in enumerate(data):
            result = f'{result}{fetch_game_data(str(index), item, int(layer + 1))}\n'
        return f"{result}{' ' * layer}]"
    elif isinstance(data, dict):
        result = f"{' ' * layer}{key}: {'{'}\n"
        for data_key in data.keys():
            result = f'{result}{fetch_game_data(data_key, data[data_key], int(layer + 1))}\n'
        return f"{result}{' ' * layer}{'}'}"
    return ''


def fetch_menu_data(key: str, menu: Menu, layer: int) -> str:
    match key:
        case 'curser':
            return f"curser:{f'x: {menu.curser[0]}', f'y: {menu.curser[1]}'}"
    return ''


class InfoTab(GuiElement):

    def __init__(self, position: tuple[int, int], size: tuple[int, int], console: tcod.Console = None):
        self._paused = False
        self._activated = False
        self._height = size[1]
        self._width = size[0]
        self._position = position
        self._console = console
        self._player_data: list[str] = []
        self._menu_data: list[tuple[str, str]] = []
        self._game_data: list[str] = []

    @property
    def player_data(self) -> list[str]:
        return self._player_data

    @player_data.setter
    def player_data(self, new_player_data: list[str]):
        self._player_data = new_player_data

    @property
    def game_data(self) -> list[str]:
        return self._player_data

    @game_data.setter
    def game_data(self, new_game_data: list[str]):
        self._game_data = new_game_data

    @property
    def menu_data(self) -> list[tuple[str, str]]:
        return self._menu_data

    @menu_data.setter
    def menu_data(self, new_menu_data: list[tuple[str, str]]):
        self._menu_data = new_menu_data

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

    def fetch_player_data(self, key: str, player: CreatureToken, layer: int) -> str: pass

    def render(self, menus: dict[str: Menu], player: CreatureToken, data_table: dict[str: any]):
        if self._activated:
            data_to_display = []
            for key, menu in self._menu_data:
                data_to_display.append(fetch_menu_data(menu, menus.menus[key], 0))
            for item in self._player_data:
                data_to_display.append(self.fetch_player_data(item, player, 0))
            for item in self._game_data:
                data_to_display.append(fetch_game_data(item, data_table[item], 0))
            text_to_print = ''
            for item in data_to_display:
                if item is None:
                    continue
                text_to_print = f'{text_to_print}\n{item}'
            x, y = self._position
            self._console.print(x=x, y=y, string=text_to_print)
