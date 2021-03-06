from __future__ import annotations
from map_token import CreatureToken


class Tile:

    def __init__(self, position: tuple[int, int], tile_type: dict[str, any] = None):
        self._position = position
        self._token_list: dict[str, CreatureToken] = {}
        if 'movement_cost' in tile_type:
            self._movement_cost = tile_type['movement_cost']
        else:
            self._movement_cost = 1
        if 'passable' in tile_type:
            self._passable = tile_type['passable']
        else:
            self._passable = True
        if 'icon' in tile_type:
            self._icon = tile_type['icon']
        else:
            self._icon = 0
        if 'description' in tile_type:
            self._description = tile_type['description']
        else:
            self._description = 'err: no description found'

    @property
    def icon(self) -> int:
        return self._icon

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, new_position: tuple(int, int)):
        self._position = new_position

    @property
    def movement_cost(self) -> int:
        if self._passable:
            return self._movement_cost
        else:
            return 1000

    @property
    def passable(self) -> bool:
        return self._passable

    @property
    def description(self):
        return self._description

    @property
    def tokens_list(self) -> dict[str, CreatureToken]:
        return self._token_list

    def add_token(self, new_token: CreatureToken):
        self._token_list[new_token.name] = new_token

    def get_token(self, token_name: str) -> CreatureToken:
        if token_name in self._token_list:
            return self._token_list[token_name]

    def remove_token(self, token_name: str):
        self._token_list.pop(token_name)
