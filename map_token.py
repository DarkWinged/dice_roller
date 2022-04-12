from character_sheet import CharacterSheet
from color import Color


class CreatureToken:
    def __init__(self, name: str, position: tuple[int, int], sheet: CharacterSheet):
        self._name = name
        self._sheet = sheet
        self._position = position
        self._actions = {'standard': True, 'movement': True, 'reaction': True}

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, new_position: tuple[int, int]):
        self._position = new_position

    @property
    def speed(self):
        return 5

    @property
    def action_standard(self): pass

    @property
    def action_movement(self):
        return self._actions['movement']

    @property
    def action_bonus(self): pass

    @property
    def action_reaction(self): pass

    @property
    def character_sheet(self): pass

    def convert_standard_to_movement(self): pass

    def roll_initiative(self) -> int:
        return self._sheet.roll_initiative()

    def render(self):
        return 'P', Color(0.6, 0.1, 0.2), Color(0.2, 0.1, 0.8)

    def take_turn(self): pass

    def valid_movements(self): pass

    def take_movement_action(self): pass

    def valid_targets(self): pass

    def __str__(self) -> str:
        return f'map_token{self._name, self._position, self._actions, self.character_sheet}'
