from map_token import CreatureToken
import room
from room import Room


def test_draw_tiles_in_circle():
    radius = 3
    offset = (3, 3)
    x_offset, y_offset = offset

    tiles = room.find_tiles_in_circle(radius, offset)

    for tile in tiles:
        x, y = tile[0] - x_offset, tile[1] - y_offset
        assert x**2 + y**2 <= radius**2


def test_render_room():
    tile_set = ['E', 'F', 'W']
    size = (5, 5)
    box = Room(1234, size, tile_set)
    test_string = ''

    for x in range(size[0]):
        for y in range(size[1]):
            test_string = f'{test_string}{tile_set[1]}'
        test_string = f'{test_string}\n'

    assert f'{box}' == test_string


def test_add_tiles():
    tile_set = ['E', 'F', 'W']
    size = (5, 5)
    test_room = Room(1234, size, tile_set)
    test_string = 'FFFFF\n' \
                  'FFFFF\n' \
                  'FFWWW\n' \
                  'FFWFF\n' \
                  'FFFFF\n'

    test_room.add_tile((4, 2), {'icon': 1, 'passable': False})
    test_room.add_tile((3, 2), {'icon': 1, 'passable': False})
    test_room.add_tile((2, 2), {'icon': 1, 'passable': False})
    test_room.add_tile((2, 3), {'icon': 1, 'passable': False})

    assert f'{test_room}' == test_string


def test_flood_fill():
    tile_set = {
                'E': {'icon': -1},
                'F': {'icon': 0},
                'W': {'icon': 1, 'passable': False},
                'R': {'icon': 2, 'movement_cost': 2}
                }
    tile_map = [
                ['W', 'W', 'W', 'F', 'W', 'W', 'W'],
                ['W', 'F', 'W', 'F', 'R', 'F', 'W'],
                ['W', 'F', 'W', 'F', 'R', 'F', 'W'],
                ['W', 'F', 'W', 'F', 'R', 'F', 'W'],
                ['W', 'F', 'F', 'F', 'F', 'F', 'W'],
                ['W', 'F', 'F', 'F', 'F', 'F', 'W'],
                ['W', 'W', 'W', 'W', 'W', 'W', 'W']
               ]
    test_room = Room.new(5678, tile_set, tile_map)
    fill_start = (3, 0)
    fill_range = 4
    result_expected = [fill_start, (3, 1), (3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (5, 1)]

    fill = test_room.flood_fill(fill_start, fill_range)

    for point in result_expected:
        assert point in fill.keys()


def test_new_map():
    tile_set = {'E': {'icon': -1}, 'F': {'icon': 0}, 'W': {'icon': 1, 'passable': False}}
    tile_map = [
                ['W', 'W', 'F', 'W', 'W'],
                ['F', 'F', 'F', 'F', 'W'],
                ['W', 'W', 'F', 'F', 'F'],
                ['E', 'W', 'F', 'F', 'W'],
                ['E', 'W', 'F', 'W', 'W']
               ]
    result = ''

    test_room = Room.new(1234, tile_set, tile_map)

    for y, column in enumerate(tile_map):
        for x, tile in enumerate(column):
            result = f'{result}{tile}'
        result = f'{result}\n'

    assert f'{test_room}' == result
    for y, column in enumerate(tile_map):
        for x, tile in enumerate(column):
            print((x, y), test_room._tile_set[test_room.tiles[(x, y)].icon], tile)
            assert test_room._tile_set[test_room.tiles[(x, y)].icon] == tile


def test_add_token():
    bob_name = 'bob'
    bob_start = (0, 0)
    bob_token = CreatureToken(bob_name, bob_start, {})
    dan_name = 'dan'
    dan_start = (5, 5)
    dan_token = CreatureToken(dan_name, dan_start, {})
    tile_set = ['E', 'F', 'W']
    size = (5, 5)
    test_map = Room(5678, size, tile_set)

    test_map.add_token(bob_token)
    test_map.add_token(bob_token)
    test_map.add_token(dan_token)

    assert bob_token in test_map.tokens.values()
    assert dan_token in test_map.tokens.values()


def test_move_token():
    token_name = 'fred'
    initial_position = (1, 1)
    test_token = CreatureToken(token_name, initial_position, {})
    tile_set = ['E', 'F', 'W']
    size = (5, 5)
    test_map = Room(5678, size, tile_set)
    movement = (1, -1)

    test_map.add_token(test_token)
    test_map.move_token(token_name, movement)

    assert test_map.tokens[token_name].position[0] == initial_position[0] + movement[0]
    assert test_map.tokens[token_name].position[1] == initial_position[1] + movement[1]


def test_path_finding():
    pass
