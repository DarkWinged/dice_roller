class MapToken:
    def __init__(self, name: str, position: tuple[int, int]):
        self._name = name
        self._position = position
        self._actions = {'standard': True, 'movement': True, 'reaction': True}

    @property
    def name(self) -> str:
        return self._name

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

    def render(self): pass

    def take_turn(self): pass

    def valid_movements(self): pass

    def take_movement_action(self): pass

    def valid_targets(self): pass

