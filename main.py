import argparse
import threading
import time

import tcod
from tcod import Console
from tcod.tileset import Tileset

from character_sheet import CharacterSheet, StatBlock
from character_sheet.enums import ability_score_iterator, AbilityScore
from color import Color
from map_renderer import MapRenderer
from map_token import CreatureToken
from menu import Menu
from room import Room
from tile import Tile
from turn_tracker import TurnTracker


def init_parser():
    new_parser = argparse.ArgumentParser(description='Launch a simple rougelike adventure game.')
    new_parser.add_argument('-w', '--window_size', dest='window_size', default='80x50', type=str,
                            help='Set the window size')
    return new_parser


def init_game():
    room = init_room()
    renderer = init_renderer()
    tcod_tile_set = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = init_player(room.tiles)

    return renderer, room, tcod_tile_set, player


def init_room():
    game_tile_set = {
        'E': {'icon': -1, 'description': 'An empty void...'},
        'F': {'icon': 0, 'description': 'A patch of smooth stone floor.'},
        'W': {'icon': 1, 'passable': False, 'description': 'A solid brick wall.'},
        'R': {'icon': 2, 'movement_cost': 2, 'description': 'A pile of rubble littering the floor.'},
        'U': {'icon': 3, 'description': 'A staircase leading up to the surface.'},
        'D': {'icon': 4, 'description': 'A staircase leading down deeper into the dungeon.'}
    }

    tile_map = [
        ['W', 'W', 'W', 'W', 'W', 'W', 'W'],
        ['W', 'D', 'W', 'U', 'R', 'F', 'W'],
        ['W', 'F', 'W', 'F', 'R', 'F', 'W'],
        ['W', 'F', 'W', 'F', 'R', 'F', 'W'],
        ['W', 'F', 'F', 'F', 'F', 'F', 'W'],
        ['W', 'F', 'F', 'E', 'E', 'F', 'W'],
        ['W', 'W', 'W', 'W', 'W', 'W', 'W'],
        ['W', 'F', 'W', 'F', 'R', 'F', 'W'],
        ['W', 'W', 'W', 'W', 'F', 'F', 'W'],
        ['W', 'F', 'W', 'E', 'E', 'F', 'W'],
        ['W', 'W', 'W', 'W', 'W', 'W', 'W']
    ]
    return Room.new(5678, game_tile_set, tile_map)


def init_renderer():
    renderer = MapRenderer()
    wall_fg, wall_bg = Color(0.1, 0.2, 0.3), Color(0.1, 0.1, 0.2)
    renderer.add_rule('W', 'fftt', renderer.pipe_symbols[0], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'tfft', renderer.pipe_symbols[1], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'ttff', renderer.pipe_symbols[2], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'fttf', renderer.pipe_symbols[3], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'ttft', renderer.pipe_symbols[4], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'fttt', renderer.pipe_symbols[5], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'tftt', renderer.pipe_symbols[6], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'tttf', renderer.pipe_symbols[7], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'tttt', renderer.pipe_symbols[8], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'ftft', renderer.pipe_symbols[9], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'ftff', renderer.pipe_symbols[9], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'ffft', renderer.pipe_symbols[9], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'tftf', renderer.pipe_symbols[10], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'tfff', renderer.pipe_symbols[10], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('W', 'fftf', renderer.pipe_symbols[10], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('F', 'a', renderer.block_symbols[2], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('R', 'a', renderer.block_symbols[0], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('U', 'a', renderer.block_symbols[4], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('D', 'a', renderer.block_symbols[3], foreground=wall_fg, background=wall_bg)
    renderer.add_rule('E', 'a', ' ', foreground=wall_fg, background=wall_bg)
    renderer.position = (17, 0)
    return renderer


def init_player(tiles: dict[tuple[int, int], Tile]):
    player_start = [position for position in tiles.keys() if tiles[position].icon == 3][0]
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race_modifiers[AbilityScore.STR] += 4
    race = {'ability_mod': race_modifiers}
    player_sheet = CharacterSheet(StatBlock(scores), race, 'fighter')
    return CreatureToken('player_name', player_start, player_sheet)


def quit_game(current_game_state: dict[str, bool]) -> None:
    print('Shutting down game')
    current_game_state['running'] = False


def move_token(creature: CreatureToken, map: Room) -> None:
    pass


def render_loop(current_game_state: dict[str, bool], console: Console, menu: Menu, room: Room, renderer: MapRenderer, tracker: TurnTracker):
    if current_game_state['fps_uncapped']:
        fps = 1000000
    elif current_game_state['fps']:
        fps = current_game_state['fps']
    else:
        fps = 30
    time_delta = 1.0 / fps
    t1, t2 = 1.0, 2.0

    while current_game_state['running']:
        menu.render(console)
        tokens = {}
        for t in tracker.tokens:
            tokens[f'({t.position[0]},{t.position[1]})'] = t
        renderer.render(console, room.stringify(), tokens)
        t2 = time.time()
        delta_time = 1.0/(t2 - t1)
        console.print(x=0, y=0, string=f'FPS:{delta_time: 0.2f}')
        t1 = time.time()
        time.sleep(time_delta)
        console.clear()


def game_loop(current_game_state: dict[str, any], console: Console, tcod_tile_set: Tileset):
    with tcod.context.new_terminal(
            console.width,
            console.height,
            tileset=tcod_tile_set,
            title="Yet Another Roguelike Game",
            vsync=True,
    ) as context:

        while current_game_state['running']:

            context.present(console)

            for event in tcod.event.wait(1.0 / current_game_state['fps']):
                context.convert_event(event)
                match event:
                    case tcod.event.Quit():
                        quit_game(current_game_state)
                    case tcod.event.KeyDown():
                        match event.sym:
                            case tcod.event.K_UP:
                                menu.curser_up()
                            case tcod.event.K_DOWN:
                                menu.curser_down()
                            case tcod.event.K_RETURN:
                                print(menu.menu_options[menu.curser_key])
                                menu.select()
                            case tcod.event.K_ESCAPE:
                                quit_game(current_game_state)
                        print(f"KeyDown: {event}")
                    case tcod.event.MouseButtonDown():
                        print(f"MouseButtonDown: {event}")
                    case tcod.event.MouseMotion():
                        print(f"MouseMotion: {event}")
                    case tcod.event.Event() as event:
                        print(event)


if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()

    init_window_size = args.window_size.split(sep='x')
    if init_window_size is None:
        screen_width = 80
        screen_height = 50
    else:
        screen_width, screen_height = [int(index) for index in init_window_size]

    root_console = tcod.Console(screen_width, screen_height, order="F")
    game_state = {'running': True, 'fps': 30, 'fps_uncapped': False}
    game_renderer, game_room, game_tcod_tile_set, player_token = init_game()

    menu = Menu((1, 1))
    menu.add_command(game_state, name='quit', command=quit_game)
    menu.add_command(player_token, game_room, name='move', command=move_token)

    tracker = TurnTracker(1234)
    tracker.add_token(player_token)

    render_thread = threading.Thread(target=render_loop,
                                     args=(game_state, root_console, menu, game_room, game_renderer, tracker))
    control_thread = threading.Thread(target=game_loop, args=(game_state, root_console, game_tcod_tile_set))

    render_thread.start()
    control_thread.start()
    control_thread.join()
    render_thread.join()
