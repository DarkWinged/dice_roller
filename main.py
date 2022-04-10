import argparse
import threading
import time

import tcod
from tcod.tileset import Tileset

from character_sheet import CharacterSheet, StatBlock
from character_sheet.enums import ability_score_iterator, AbilityScore
from color import Color
from game_state import GameState
from map_renderer import MapRenderer
from map_token import CreatureToken
from menu import MainMenu, Menu, MovementMenu
from menu_commands import quit_game, open_movement_menu, cancel_selection, confirm_selection
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
    player = init_player(room.tiles)
    tcod_tile_set = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    return init_renderer(), room, tcod_tile_set, player, init_tracker(player)


def init_room():
    game_tile_set = {
        'E': {'icon': -1, 'passable': False, 'description': 'An empty void...'},
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
    renderer = MapRenderer((0, 0), (20, 20))
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
    renderer.position = (17, 1)
    return renderer


def init_player(tiles: dict[tuple[int, int], Tile]):
    player_start = [position for position in tiles.keys() if tiles[position].icon == 3][0]
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race_modifiers[AbilityScore.STR] = 0
    race = {'ability_mod': race_modifiers}
    player_sheet = CharacterSheet(StatBlock(scores), race, 'fighter')
    return CreatureToken('player_name', player_start, player_sheet)


def init_tracker(token: CreatureToken):
    new_tracker = TurnTracker(1234)
    new_tracker.add_token(token)
    return new_tracker


def render_loop(current_game_state: GameState, void: None = None):
    if current_game_state.fps_uncapped:
        fps = 1000000
    elif current_game_state.fps:
        fps = current_game_state.fps
    else:
        fps = 30
    time_delta = 1.0 / fps
    t1, t2 = 1.0, 2.0

    while current_game_state.running:
        console = current_game_state.console
        renderer = current_game_state.renderer
        menu_names = current_game_state.menus.keys()
        menus: list[Menu] = [m for m in current_game_state.menus.values() if m.activated]
        for menu_to_render in menus:
            if 'selection' in menu_names and menu_to_render is current_game_state.menus['selection']:
                renderer.curser = menu_to_render.curser
                if menu_to_render.curser in current_game_state.rooms[current_game_state.current_room].tiles and renderer.activated:
                    hovered_tile = current_game_state.rooms[current_game_state.current_room].tiles[menu_to_render.curser].description
                    menu_to_render.render(hovered_tile)
            else:
                menu_to_render.render()
        renderer.render()
        t2 = time.time()
        delta_time = 1.0 / (t2 - t1)

        if delta_time >= fps / 2:
            fps_color = (255, 255, 255)
        elif delta_time >= fps / 5:
            fps_color = (255, 255, 0)
        else:
            fps_color = (255, 0, 0)

        console.print(x=int(console.width / 2), y=0, string=f'FPS:{delta_time: 0.2f}', fg=fps_color, alignment=2)
        t1 = time.time()
        time.sleep(time_delta)
        console.clear()


def game_loop(current_game_state: GameState, tcod_tile_set: Tileset):
    console = current_game_state.console
    with tcod.context.new_terminal(
            console.width,
            console.height,
            tileset=tcod_tile_set,
            title="Yet Another Roguelike Game",
            vsync=True,
    ) as context:
        while current_game_state.running:
            menus: list[Menu] = [m for m in current_game_state.menus.values() if m.activated and not m.paused]
            context.present(console)
            for menu_to_process in menus:
                menu_to_process.process(current_game_state.fps, context)


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
    game_renderer, game_room, game_tcod_tile_set, player_token, tracker = init_game()
    game_state = GameState(
        True,
        30,
        False,
        {},
        [game_room],
        0,
        tracker,
        player_token,
        game_renderer,
        root_console
    )

    main_menu = MainMenu((1, 1), (14, 20), root_console)
    main_menu.add_command(game_state, name='quit', command=quit_game)
    main_menu.add_command(game_state, name='move', command=open_movement_menu)
    selection = MovementMenu((16, 22), (40, 10), root_console)
    selection.add_command(game_state, name='quit', command=quit_game)
    selection.add_command(game_state, name='cancel', command=cancel_selection)
    selection.add_command(game_state, name='confirm', command=confirm_selection)

    game_state.menus['main'] = main_menu
    game_state.menus['selection'] = selection
    game_state.renderer.canvas = root_console
    game_state.renderer.activate()
    game_state.renderer.load_tiles(game_state.rooms[0].stringify())
    game_state.renderer.load_entities(game_state.turn_tracker.tokens)

    render_thread = threading.Thread(target=render_loop, args=(game_state, None))
    control_thread = threading.Thread(target=game_loop, args=(game_state, game_tcod_tile_set))

    main_menu.activate()
    render_thread.start()
    control_thread.start()
    control_thread.join()
    render_thread.join()
