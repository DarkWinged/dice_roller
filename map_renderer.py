from tcod import Console

from color import Color
from map_token import CreatureToken


class MapRenderer:
    block_symbols = ['░', '▒', '▓', '▐', '▀']
    pipe_symbols = ['╗', '╝', '╚', '╔', '╩', '╦', '╣', '╠', '╬', '═', '║']
    line_symbols = ['┐', '┘', '└', '┌', '┴', '┬', '┤', '├', '┼', '─', '│']

    def __init__(self):
        self._position = (0, 0)
        self.rules = {}

    @property
    def position(self) -> (int, int):
        return self._position

    @position.setter
    def position(self, pos: tuple[int, int]):
        self._position = pos

    def add_rule(self, tile: str, rule: str, sub: str, /, *, foreground: Color = None,
                 background: Color = None):
        if foreground is None:
            foreground = Color(255, 255, 255)
        if background is None:
            background = Color(0, 0, 0)

        new_rule = {rule: sub, 'foreground': foreground, 'background': background}
        if tile in self.rules.keys():
            if new_rule not in self.rules[tile]:
                self.rules[tile].append(new_rule)
        else:
            self.rules[tile] = [new_rule]

    def render(self, root_console: Console, tiles: str, entities: dict[str: CreatureToken], curser: tuple[int, int],
               highlighted: list[tuple[int, int]] = None):
        if highlighted is None:
            highlighted = [(-1, -1)]
        rows = tiles.split(sep='\n')
        while '' in rows:
            rows.remove('')

        height = len(rows)
        width = len(rows[0])
        ruled_tiles = []
        x_offset, y_offset = self.position

        for y in range(height):
            ruled_tiles.append([])
            for x in range(width):
                tile = rows[y][x]
                if tile in self.rules.keys():
                    foreground: Color
                    background: Color
                    inverted = False
                    shifted = 0
                    if f'({x},{y})' == f'({curser[0]},{curser[1]})':
                        inverted = True
                    if (x, y) in highlighted:
                        shifted = 1
                    if f'({x},{y})' in entities.keys():
                        tile, foreground, background = entities[f'({x},{y})'].render()
                        root_console.print(x=x+x_offset, y=y+y_offset, string=tile,
                                           fg=foreground.rgb(invert=inverted, shift=shifted),
                                           bg=background.rgb(invert=inverted, shift=shifted)
                                           )
                    else:
                        tile, foreground, background = self.apply_rules((x, y), (width, height), rows)
                        root_console.print(x=x+x_offset, y=y+y_offset, string=tile,
                                           fg=foreground.rgb(invert=inverted, shift=shifted),
                                           bg=background.rgb(invert=inverted, shift=shifted)
                                           )

    def apply_rules(self, position: tuple[int, int], limits: tuple[int, int], rows: list[str]) ->\
            (str, Color, Color):
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

        for rule in rules:
            if sample in rule:
                return rule[sample], rule['foreground'], rule['background']
        return tile, Color(1.0, 1.0, 1.0), Color(0.0, 0.0, 0.0)
