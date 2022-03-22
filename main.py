import argparse

import tcod
from tcod import Console

from map_token import CreatureToken
from room import Room


def init_parser():
    new_parser = argparse.ArgumentParser(description='Launch a simple rougelike adventure game.')
    new_parser.add_argument('-w', '--window_size', dest='window_size', default='80x50', type=str,
                            help='Set the window size')
    return new_parser


def init_game():
    game_tile_set = {
        'E': {'icon': -1, 'description': 'An empty void...'},
        'F': {'icon': 0, 'description': 'A patch of smooth stone floor.'},
        'W': {'icon': 1, 'passable': False, 'description': 'A solid brick wall.'},
        'R': {'icon': 2, 'movement_cost': 2, 'description': 'A pile of rubble littering the floor.'},
        'U': {'icon': 3, 'description': 'A staircase leading up to the surface.'},
        'D': {'icon': 4, 'description': 'A staircase leading down deeper into the dungeon.'}
    }

    renderer = MapRenderer()
    wall_fg, wall_bg = (30, 60, 120), (30, 30, 60)
    renderer.add_rule('W', 'fftt', renderer.pipe_symbols[0], wall_fg, wall_bg)
    renderer.add_rule('W', 'tfft', renderer.pipe_symbols[1], wall_fg, wall_bg)
    renderer.add_rule('W', 'ttff', renderer.pipe_symbols[2], wall_fg, wall_bg)
    renderer.add_rule('W', 'fttf', renderer.pipe_symbols[3], wall_fg, wall_bg)
    renderer.add_rule('W', 'ttft', renderer.pipe_symbols[4], wall_fg, wall_bg)
    renderer.add_rule('W', 'fttt', renderer.pipe_symbols[5], wall_fg, wall_bg)
    renderer.add_rule('W', 'tftt', renderer.pipe_symbols[6], wall_fg, wall_bg)
    renderer.add_rule('W', 'tttf', renderer.pipe_symbols[7], wall_fg, wall_bg)
    renderer.add_rule('W', 'tttt', renderer.pipe_symbols[8], wall_fg, wall_bg)
    renderer.add_rule('W', 'ftft', renderer.pipe_symbols[9], wall_fg, wall_bg)
    renderer.add_rule('W', 'ftff', renderer.pipe_symbols[9], wall_fg, wall_bg)
    renderer.add_rule('W', 'ffft', renderer.pipe_symbols[9], wall_fg, wall_bg)
    renderer.add_rule('W', 'tftf', renderer.pipe_symbols[10], wall_fg, wall_bg)
    renderer.add_rule('W', 'tfff', renderer.pipe_symbols[10], wall_fg, wall_bg)
    renderer.add_rule('W', 'fftf', renderer.pipe_symbols[10], wall_fg, wall_bg)
    renderer.add_rule('F', 'a', renderer.block_symbols[2], wall_fg, wall_bg)
    renderer.add_rule('R', 'a', renderer.block_symbols[0], wall_fg, wall_bg)
    renderer.add_rule('U', 'a', renderer.block_symbols[4], wall_fg, wall_bg)
    renderer.add_rule('D', 'a', renderer.block_symbols[3], wall_fg, wall_bg)
    renderer.add_rule('E', 'a', ' ', wall_fg, wall_bg)

    tcod_tile_set = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    return renderer, game_tile_set, tcod_tile_set


def loop_game(renderer, game_tile_set, tcod_tile_set, window_size=None):
    if window_size is None:
        screen_width = 80
        screen_height = 50
    else:
        screen_width, screen_height = window_size
    renderer.position = (25, 5)
    with tcod.context.new_terminal(
            screen_width,
            screen_height,
            tileset=tcod_tile_set,
            title="Yet Another Roguelike Tutorial",
            vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        running = True
        menu = Menu((1, 1), {'Move': None, 'Inventory': None, 'Exit': SystemExit})
        while running:

            context.present(root_console)
            menu.render(root_console)

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
            test_room = Room.new(5678, game_tile_set, tile_map)
            player_start = [position for position in test_room.tiles.keys() if test_room.tiles[position].icon == 3][0]
            player = CreatureToken('player_name', player_start, {})
            test_room.add_token(player)
            renderer.render(root_console, test_room.__str__())

            for event in tcod.event.wait():
                context.convert_event(event)  # Add tile coordinates to mouse events.
                match event:
                    case tcod.event.Quit():
                        raise SystemExit()
                    case tcod.event.KeyDown():
                        match event.sym:
                            case tcod.event.K_UP:
                                menu.curser_up()
                            case tcod.event.K_DOWN:
                                menu.curser_down()
                            case tcod.event.K_SPACE:
                                print(menu.menu_options[menu.curser_key])
                                menu.select(player, test_room)
                            case tcod.event.K_ESCAPE:
                                raise SystemExit()

                        print(f"KeyDown: {event}")
                    case tcod.event.MouseButtonDown():
                        print(f"MouseButtonDown: {event}")
                    case tcod.event.MouseMotion():
                        print(f"MouseMotion: {event}")
                    case tcod.event.Event() as event:
                        print(event)  # Show any unhandled events.


class MapRenderer:
    block_symbols = ['░', '▒', '▓', '▐', '▀']
    pipe_symbols = ['╗', '╝', '╚', '╔', '╩', '╦', '╣', '╠', '╬', '═', '║']
    line_symbols = ['┐', '┘', '└', '┌', '┴', '┬', '┤', '├', '┼', '─', '│']

    def __init__(self):
        self._position = (0, 0)
        self.rules = {}

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, pos: tuple[int, int]):
        self._position = pos

    def add_rule(self, tile: str, rule: str, sub: str, foreground: tuple[int, int, int] = None, background: tuple[int, int, int] = None):
        if foreground is None:
            foreground = (255, 255, 255)
        if background is None:
            background = (0, 0, 0)

        new_rule = {rule: sub, 'foreground': foreground, 'background': background}
        if tile in self.rules.keys():
            if new_rule not in self.rules[tile]:
                self.rules[tile].append(new_rule)
        else:
            self.rules[tile] = [new_rule]

    def render(self, root_console: Console, tiles: str):
        rows = tiles.split(sep='\n')
        rows_to_cull = []
        for index, row in enumerate(rows):
            if row == '':
                rows_to_cull.append(index)

        rows_to_cull.sort(reverse=True)
        for cull in rows_to_cull:
            rows.pop(cull)

        height = len(rows)
        width = len(rows[0])
        result = []

        for y in range(height):
            result.append([])
            for x in range(width):
                tile = rows[y][x]
                if tile in self.rules.keys():
                    result[y].append(self.apply_rules((x, y), (width, height), rows))

        x_offset, y_offset = self.position
        for y in range(height):
            for x in range(width):
                tile, foreground, background = result[y][x]
                root_console.print(x=x+x_offset, y=y+y_offset, string=tile, fg=foreground, bg=background)

        return result

    def apply_rules(self, position: tuple[int, int], limits: tuple[int, int], rows: list[str]) ->\
            (str, tuple[int, int, int]):
        x, y = position
        tile = rows[y][x]
        rules = self.rules[tile]
        x_max, y_max = limits
        sample = ''
        samples = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]

        for rule in rules:
            if 'a' in rule:
                return rule['a'], rule['foreground'], rule['background']

        for count, position in enumerate(samples):
            x_relative, y_relative = position
            if 0 <= x_relative < x_max and 0 <= y_relative < y_max:
                if rows[y_relative][x_relative] == tile:
                    sample = f'{sample}t'
                else:
                    sample = f'{sample}f'
            else:
                sample = f'{sample}f'

        if x == 7 and y == 0:
            print((x, y), samples)
        for rule in rules:
            if sample in rule:
                return rule[sample], rule['foreground'], rule['background']
        return tile, (255, 255, 255), (0, 0, 0)


class Menu:
    def __init__(self, position: tuple[int, int], options: dict[str, callable(None)]):
        self.position = position
        self.menu_options = options
        self.curser = 0

    def curser_up(self):
        self.curser -= 1
        if self.curser < 0:
            self.curser = len(self.menu_options) - 1

    def curser_down(self):
        self.curser += 1
        if self.curser >= len(self.menu_options):
            self.curser = 0

    def render(self, console: tcod.Console):
        console.clear()
        console.print(x=self.position[0], y=self.position[1], string=f" {'_' * 5}MENU{'_' * 5}")
        for item, menu_item in enumerate(self.menu_options.keys()):
            if item == self.curser:
                console.print(x=self.position[0], y=self.position[1] + item + 1, string=f'|{menu_item:<14}|',
                              fg=(0, 255, 0))
            else:
                console.print(x=self.position[0], y=self.position[1] + item + 1, string=f'|{menu_item:<14}|')

    @property
    def curser_key(self):
        return [key for index, key in enumerate(self.menu_options.keys()) if index == self.curser][0]

    def select(self, current_token: CreatureToken, current_room: Room):
        curser_key = self.curser_key
        if self.menu_options[curser_key] is SystemExit:
            raise SystemExit()
        elif self.menu_options[curser_key] is not None:
            self.menu_options[curser_key](current_token, current_room)


if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()
    init_window_size = args.window_size.split(sep='x')
    init_window_size = (int(init_window_size[0]), int(init_window_size[1]))

    init_renderer, init_game_tile_set, init_tcod_tile_set = init_game()
    loop_game(init_renderer, init_game_tile_set, init_tcod_tile_set, init_window_size)
