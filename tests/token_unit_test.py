import map_token
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


def test_move_token():
    token_name = 'fred'
    initial_position = (1, 1)
    test_token = map_token.MapToken(token_name, initial_position)
    tile_set = ['E', 'F', 'W']
    size = (5, 5)
    test_map = Room(5678, size, tile_set)
    movement = (1, -1)

    test_map.add_token(test_token)
    test_map.move_token(token_name, movement)

    assert test_map.tokens[token_name].position[0] == initial_position[0] + movement[0]
    assert test_map.tokens[token_name].position[1] == initial_position[1] + movement[1]
