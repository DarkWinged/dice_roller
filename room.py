from map_token import MapToken
from tile import Tile


def find_tiles_in_square(radius: int, offset: tuple[int, int] = None) -> list[tuple[int, int]]:
    if offset is None:
        offset = (0, 0)
    x_center, y_center = offset
    points = set()
    result = []

    for x in range(radius):
        for y in range(radius):
            x_sym = - x
            y_sym = - y
            points.add((x+x_center, y+y_center))
            points.add((x+x_center, y_sym+y_center))
            points.add((x_sym+x_center, y+y_center))
            points.add((x_sym+x_center, y_sym+y_center))
    result += list(points)

    return result


def find_tiles_in_circle(radius: int, offset: tuple[int, int] = None) -> list[tuple[int, int]]:
    if offset is None:
        offset = (0, 0)
    x_center, y_center = offset
    points = set()
    result = []

    for x in range(radius + 1):
        for y in range(radius + 1):
            if x ** 2 + y ** 2 <= radius ** 2:
                x_sym = - x
                y_sym = - y
                points.add((x+x_center, y+y_center))
                points.add((x+x_center, y_sym+y_center))
                points.add((x_sym+x_center, y+y_center))
                points.add((x_sym+x_center, y_sym+y_center))
    result += list(points)

    return result


def transfer_token(token_name: str, origin: Tile, destination: Tile):
    token_to_move = origin.get_token(token_name)
    origin.remove_token(token_to_move.name)
    destination.add_token(token_to_move)


class Room:
    def __init__(self, seed: int, size: tuple[int, int], tile_set: list[str]):
        self._tiles = {}
        self._tokens: dict[str, MapToken] = {}
        self._seed = seed
        self._size = size
        self._tile_set: dict[int, str] = {}
        for index, icon in enumerate(tile_set):
            self._tile_set[index - 1] = icon
        for x in range(size[0]):
            for y in range(size[1]):
                self._tiles[(x, y)] = Tile((x, y), {})

    @property
    def tokens(self):
        return self._tokens

    def __str__(self):
        string = ''
        for x in reversed(range(self._size[0])):
            for y in range(self._size[1]):
                if self._tiles[(x, y)].icon in self._tile_set:
                    tile_icon = self._tile_set[self._tiles[(x, y)].icon]
                else:
                    tile_icon = self._tile_set[-1]
                string = f'{string}{tile_icon}'
            string = f'{string}\n'
        return string

    def add_tile(self, position: tuple[int, int], tile_type: dict[str, any] = None):
        self._tiles[position] = Tile(position, tile_type)

    @property
    def tiles(self):
        return self._tiles

    def add_token(self, new_token: MapToken):
        if new_token.name in self._tokens.keys() and new_token is not self._tokens[new_token.name]:
            raise NameError(f'Name: {new_token.name, new_token} already exists in Room._tokens['
                            f'{self._tokens[new_token.name]}]')
        else:
            self._tokens[new_token.name] = new_token

    def move_token(self, token_name: str, movement: tuple[int, int]):
        moving_token = self._tokens[token_name]
        target = moving_token.position[0] + movement[0], moving_token.position[1] + movement[1]
        if self.validate_movement(moving_token, target):
            self._tokens[token_name].position = target

    def validate_movement(self, moving_token: MapToken, target_position: tuple[int, int]) -> bool:
        if not moving_token.action_movement:
            return False
        elif target_position not in self._tiles.keys():
            return False
        elif target_position not in find_tiles_in_circle(moving_token.speed, moving_token.position):
            return False
        else:
            return True

    def get_tokens_in_range(self):
        pass
