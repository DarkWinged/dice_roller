import tcod
from tcod import Console

from color import Color
from gui_element import GuiElement
from map_token import CreatureToken


class MapRenderer(GuiElement):
    block_symbols = ['░', '▒', '▓', '▐', '▀']
    pipe_symbols = ['╗', '╝', '╚', '╔', '╩', '╦', '╣', '╠', '╬', '═', '║']
    line_symbols = ['┐', '┘', '└', '┌', '┴', '┬', '┤', '├', '┼', '─', '│']

    def __init__(self, position: (int, int), size: (int, int), console: Console = None):
        self._width, self._height = size
        self._position = position
        self._paused = False
        self._activated = False
        self.rules = {}
        self._console = console
        self._tiles: {(int, int): (str, Color, Color)} = {}
        self._entities: {(int, int): (str, Color, Color)} = {}
        self._curser: (int, int) = None
        self._highlighted_tiles: [(int, int)] = None

    @property
    def highlighted_tiles(self) -> [(int, int)]:
        return self._highlighted_tiles

    @highlighted_tiles.setter
    def highlighted_tiles(self, new_highlighted_tiles: [(int, int)]):
        self._highlighted_tiles = new_highlighted_tiles

    @property
    def curser(self) -> (int, int):
        return self._curser

    @curser.setter
    def curser(self, new_curser: (int, int)):
        self._curser = new_curser

    @property
    def activated(self) -> bool:
        return self._activated

    def activate(self):
        self._activated = True

    def deactivate(self):
        self._activated = False

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, new_height: int):
        self._height = new_height

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, new_width: int):
        self._width = new_width

    @property
    def canvas(self) -> tcod.Console:
        return self._console

    @canvas.setter
    def canvas(self, new_canvas: Console):
        self._console = new_canvas

    @property
    def position(self) -> (int, int):
        return self._position

    @position.setter
    def position(self, new_position: tuple[int, int]):
        self._position = new_position

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

    def load_entities(self, entities: [CreatureToken]):
        self._entities = {}
        for entity in entities:
            self._entities[entity.position] = entity.render()

    def load_tiles(self, tiles: str):
        self._tiles = {}
        rows = tiles.split(sep='\n')
        while '' in rows:
            rows.remove('')
        height = len(rows)
        width = len(rows[0])

        for y in range(self._height):
            if y < len(rows):
                for x in range(self._width):
                    if x < len(rows[y]):
                        tile = rows[y][x]
                        if tile in self.rules.keys():
                            foreground: Color
                            background: Color
                            tile, foreground, background = self.apply_rules((x, y), (width, height), rows)
                            self._tiles[(x, y)] = (tile, foreground, background)
                    else:
                        rule = self.rules['E'][0]
                        self._tiles[(x, y)] = (rule['a'], rule['foreground'], rule['background'])
            else:
                for x in range(self._width):
                    rule = self.rules['E'][0]
                    self._tiles[(x, y)] = (rule['a'], rule['foreground'], rule['background'])

    def render(self):
        if self.activated:
            if self._highlighted_tiles is None:
                highlighted_tiles = [(-1, -1)]
            else:
                highlighted_tiles = self._highlighted_tiles
            if self._curser is None:
                curser = (-1, -1)
            else:
                curser = self._curser
            x_offset, y_offset = self.position

            for position in self._tiles.keys():
                x, y = position
                tile, foreground, background = self._tiles[position]
                if f'({x},{y})' == f'({curser[0]},{curser[1]})':
                    inverted = True
                else:
                    inverted = False
                if (x, y) in highlighted_tiles:
                    shifted = 1
                else:
                    shifted = 0
                if position in self._entities.keys():
                    tile, foreground, background = self._entities[position]
                    self._console.print(x=x + x_offset,
                                        y=y + y_offset,
                                        string=tile,
                                        fg=foreground.rgb(invert=inverted, shift=shifted),
                                        bg=background.rgb(invert=inverted, shift=shifted)
                                        )
                else:
                    self._console.print(x=x + x_offset,
                                        y=y + y_offset,
                                        string=tile,
                                        fg=foreground.rgb(invert=inverted, shift=shifted),
                                        bg=background.rgb(invert=inverted, shift=shifted)
                                        )

    def apply_rules(self, position: tuple[int, int], limits: tuple[int, int], rows: list[list[str]]) -> \
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
