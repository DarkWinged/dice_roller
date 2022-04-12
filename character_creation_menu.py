import math

import tcod
from tcod.context import Context

from character_sheet.enums import AbilityScore
from color import Color
from menus import Menu, MenuCommand, ListedMenu


def find_max_length(keys: list[AbilityScore]) -> int:
    max_length = 0
    for key in keys:
        key_length = len(str(key.value))
        if key_length > max_length:
            max_length = key_length
    return max_length


class RaceSelectionMenu(ListedMenu): pass


class AbilityScoreMenu(Menu):

    def __init__(self, position: tuple[int, int], size: tuple[int, int], console: tcod.Console = None):
        self._position = position
        self._width = size[0]
        self._height = size[1]
        self.menu_options: dict[str, MenuCommand] = {}
        self._curser = (0, 0)
        self._activated = False
        self._paused = False
        self._console = console
        self._key_codes = {
            'UP': tcod.event.K_UP,
            'DOWN': tcod.event.K_DOWN,
            'LEFT': tcod.event.K_LEFT,
            'RIGHT': tcod.event.K_RIGHT
        }
        self._ability_table = {}
        self._free_points = 0

    @property
    def free_points(self) -> int:
        return self._free_points

    @free_points.setter
    def free_points(self, new_free_points: int):
        self._free_points = new_free_points

    @property
    def data_table(self) -> dict[str: any]:
        return self._ability_table

    @data_table.setter
    def data_table(self, new_data_table: dict[str: any]):
        self._ability_table = new_data_table

    def curser_up(self):
        self._curser = (self._curser[0], self._curser[1] - 1)
        if self._curser[1] < 0:
            self._curser = (self._curser[0], len(self._ability_table.keys()) - 1)

    def curser_down(self):
        self._curser = (self._curser[0], self._curser[1] + 1)
        if self._curser[1] >= len(self._ability_table.keys()):
            self._curser = (self._curser[1], 0)

    def curser_left(self):
        key_list = list(self._ability_table.keys())
        self.decrement_value(key_list[self.curser[1]])

    def decrement_value(self, key: str):
        if self._ability_table[key] > 8:
            self._ability_table[key] -= 1

    def curser_right(self):
        key_list = list(self._ability_table.keys())
        self.increment_value(key_list[self.curser[1]])

    def increment_value(self, key: str):
        self._ability_table[key] += 1
        if self._ability_table[key] > 16 or self.ability_score_cost() > self.free_points:
            self._ability_table[key] -= 1

    def ability_score_cost(self) -> int:
        total = 0
        for score in self._ability_table.values():
            if math.floor((score - 10)/2) < 2:
                total += score - 8
            else:
                total += 5 + (score - 13) * 2
        return total

    def render(self):
        if self._activated:
            color: Color
            x, y = self._position
            color = Color(1.0, 0.0, 0.0)
            self._console.print(
                x=x,
                y=y,
                string=f"points remaining: {self._free_points - self.ability_score_cost()}",
                fg=color.rgb()
            )
            max_length = find_max_length(self._ability_table.keys())
            for item, data_item in enumerate(self._ability_table.keys()):
                if item == self._curser[1] and not self.paused:
                    color = Color(0.0, 1.0, 0.0)
                else:
                    color = Color(1.0, 1.0, 1.0)
                data_name: AbilityScore = data_item
                self._console.print(
                    x=x,
                    y=y + item + 1,
                    string=f"{data_name.value}{' ' * (max_length- len(str(data_name.value)))}: {self._ability_table[data_item]}",
                    fg=color.rgb()
                )

    def process(self, fps: int, context: Context):
        if self._activated and not self._paused:
            for event in tcod.event.wait(1.0 / fps):
                context.convert_event(event)
                match event:
                    case tcod.event.Quit():
                        print(f"KeyDown: {event}")
                        menu_command = self.menu_options['quit'.upper()]
                        print(f'MenuCommand{menu_command.name, menu_command.command}')
                        menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
                    case tcod.event.KeyDown():
                        print(f"KeyDown: {event}")
                        if event.sym == self._key_codes['UP']:
                            self.curser_up()
                        elif event.sym == self._key_codes['DOWN']:
                            self.curser_down()
                        if event.sym == self._key_codes['LEFT']:
                            self.curser_left()
                        elif event.sym == self._key_codes['RIGHT']:
                            self.curser_right()
                        elif event.sym == tcod.event.K_RETURN:
                            menu_command = self.menu_options['confirm'.upper()]
                            print(f'MenuCommand{menu_command.name, menu_command.command}')
                            menu_command.command(self._ability_table, *menu_command.positional_args,
                                                 **menu_command.keyword_args)
                        elif event.sym == tcod.event.K_ESCAPE:
                            menu_command = self.menu_options['cancel'.upper()]
                            print(f'MenuCommand{menu_command.name, menu_command.command}')
                            menu_command.command(*menu_command.positional_args, **menu_command.keyword_args)
