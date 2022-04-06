from map_token import CreatureToken
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


def get_neighbors(point: tuple[int, int]) -> tuple[tuple[int, int], list[tuple[int, int]]]:
    return point, [(point[0]+1, point[1]), (point[0], point[1]+1), (point[0]-1, point[1]), (point[0], point[1]-1)]


class Room:
    def __init__(self, seed: int, size: tuple[int, int], tile_set: list[str],
                 tile_map: dict[tuple[int, int], Tile] = None):
        if tile_map is None:
            self._tiles = {}
            for x in range(size[0]):
                for y in range(size[1]):
                    self._tiles[(x, y)] = Tile((x, y), {})
        else:
            self._tiles = tile_map
        self._seed = seed
        self._size = size
        self._tile_set: dict[int, str] = {}
        for index, icon in enumerate(tile_set):
            self._tile_set[index - 1] = icon

    @classmethod
    def new(cls, seed: int, tile_set: dict[str, dict[str, any]], tile_map: list[list[str]]):
        length_y, length_x = len(tile_map), max([len(column) for column in tile_map])
        size = (length_x, length_y)
        tiles = {}
        for y in range(len(tile_map)):
            for x in range(len(tile_map[0])):
                tiles[(x, y)] = Tile((x, y), tile_set[tile_map[y][x]])
        new_room = Room(seed, size, tile_set.keys(), tiles)
        return new_room

    def stringify(self):
        string = ''
        for y in range(self._size[1]):
            for x in range(self._size[0]):
                if (x, y) in self._tiles and self._tiles[(x, y)].icon in self._tile_set:
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

    def flood_fill(self, start: tuple[int, int], movement_points: int) -> list[tuple[int, int]]:
        fill = {}
        neighbors = {}
        if start in self._tiles:
            fill[start] = movement_points
            point, adjacent = get_neighbors(start)
            neighbors[point] = adjacent
            while len(neighbors) != 0:
                points = []
                for point in neighbors.keys():
                    points.append(point)
                for point in points:
                    adjacent = neighbors.pop(point)
                    for neighbor in adjacent:
                        if neighbor in self._tiles and self._tiles[neighbor].passable is True and\
                                fill[point] - self._tiles[neighbor].movement_cost >= 0:
                            fill[neighbor] = fill[point] - self._tiles[neighbor].movement_cost
                            new_point, adjacent = get_neighbors(neighbor)
                            neighbors[new_point] = adjacent
        return fill

    def get_tokens_in_range(self):
        pass
