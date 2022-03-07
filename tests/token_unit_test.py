from map_token import MapToken
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
    test_string = 'FFWFF\n' \
                  'FFWFF\n' \
                  'FFWWF\n' \
                  'FFFFF\n' \
                  'FFFFF\n'

    test_room.add_tile((4, 2), {'icon': 1, 'passable': False})
    test_room.add_tile((3, 2), {'icon': 1, 'passable': False})
    test_room.add_tile((2, 2), {'icon': 1, 'passable': False})
    test_room.add_tile((2, 3), {'icon': 1, 'passable': False})

    assert f'{test_room}' == test_string


def test_add_token():
    bob_name = 'bob'
    bob_start = (0, 0)
    bob_token = MapToken(bob_name, bob_start)
    dan_name = 'dan'
    dan_start = (5, 5)
    dan_token = MapToken(dan_name, dan_start)
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
    test_token = MapToken(token_name, initial_position)
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
