import pygame
import tcod
from pygame.constants import KEYDOWN, K_ESCAPE

from map_token import CreatureToken
from room import Room


def game_init():
    game_tile_set = {
        'E': {'icon': -1, 'description': 'An empty void...'},
        'F': {'icon': 0, 'description': 'A patch of smooth stone floor.'},
        'W': {'icon': 1, 'passable': False, 'description': 'A solid brick wall.'},
        'R': {'icon': 2, 'movement_cost': 2, 'description': 'A pile of rubble littering the floor.'},
        'U': {'icon': 3, 'description': 'A staircase leading up to the surface.'},
        'D': {'icon': 4, 'description': 'A staircase leading down deeper into the dungeon.'}
    }

    renderer = MapRenderer()
    renderer.add_rule('W', 'fftt', renderer.pipe_syms[0])
    renderer.add_rule('W', 'tfft', renderer.pipe_syms[1])
    renderer.add_rule('W', 'ttff', renderer.pipe_syms[2])
    renderer.add_rule('W', 'fttf', renderer.pipe_syms[3])
    renderer.add_rule('W', 'ttft', renderer.pipe_syms[4])
    renderer.add_rule('W', 'fttt', renderer.pipe_syms[5])
    renderer.add_rule('W', 'tftt', renderer.pipe_syms[6])
    renderer.add_rule('W', 'tttf', renderer.pipe_syms[7])
    renderer.add_rule('W', 'tttt', renderer.pipe_syms[8])
    renderer.add_rule('W', 'ftft', renderer.pipe_syms[9])
    renderer.add_rule('W', 'ftff', renderer.pipe_syms[9])
    renderer.add_rule('W', 'ffft', renderer.pipe_syms[9])
    renderer.add_rule('W', 'tftf', renderer.pipe_syms[10])
    renderer.add_rule('W', 'tfff', renderer.pipe_syms[10])
    renderer.add_rule('W', 'fftf', renderer.pipe_syms[10])
    renderer.add_rule('F', 'a', renderer.block_syms[2])
    renderer.add_rule('R', 'a', renderer.block_syms[0])
    renderer.add_rule('U', 'a', renderer.block_syms[4])
    renderer.add_rule('D', 'a', renderer.block_syms[3])
    renderer.add_rule('E', 'a', ' ')

    tcod_tile_set = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    return renderer, game_tile_set, tcod_tile_set


def game_loop(renderer, game_tile_set, tcod_tile_set):
    screen_width = 80
    screen_height = 50

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
            root_console.print(x=25, y=5, string=f"{renderer.render(test_room.__str__())}")

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
    block_syms = ['░', '▒', '▓', '▐', '▀']
    pipe_syms = ['╗', '╝', '╚', '╔', '╩', '╦', '╣', '╠', '╬', '═', '║']
    line_syms = ['┐', '┘', '└', '┌', '┴', '┬', '┤', '├', '┼', '─', '│']

    def __init__(self):
        self.rules = {}

    def add_rule(self, tile: str, rule: str, sub: str):
        new_rule = {rule: sub}
        if tile in self.rules.keys():
            if new_rule not in self.rules[tile]:
                self.rules[tile].append(new_rule)
        else:
            self.rules[tile] = [new_rule]

    def render(self, tiles: str):
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
        result = ''

        for y in range(height):
            for x in range(width):
                tile = rows[y][x]
                if tile in self.rules.keys():
                    tile = self.apply_rules((x, y), (width, height), rows)
                result = f'{result}{tile}'
            result = f'{result}\n'

        return result

    def apply_rules(self, position: tuple[int, int], limits: tuple[int, int], rows: list[str]) -> str:
        x, y = position
        tile = rows[y][x]
        rules = self.rules[tile]
        x_max, y_max = limits
        sample = ''
        samples = [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]

        for rule in rules:
            if 'a' in rule:
                return rule['a']

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
                return rule[sample]
        return tile


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
    init_renderer, init_game_tile_set, init_tcod_tile_set = game_init()
    game_loop(init_renderer, init_game_tile_set, init_tcod_tile_set)
