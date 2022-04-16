from die import Dice
from map_token import CreatureToken


class TurnTracker:
    def __init__(self, seed: int):
        self._tokens: dict[str, CreatureToken] = {}
        self._initiative_order: dict[float, str] = {}
        self._die = Dice('1d10', seed)

    @property
    def tokens(self) -> dict[str, CreatureToken]:
        return self._tokens

    def add_token(self, new_token: CreatureToken) -> str:
        if len(self._tokens.keys()) == 0:
            key = None
        else:
            key = list(self._tokens.keys())[0]
        if new_token not in self._tokens.values() or key is None:
            while key in self._tokens.keys() or key is None:
                for iterations in range(16):
                    roll = self._die.roll()
                    key = f'{key}{roll[0]-1}'
            self._tokens[key] = new_token
            self.add_to_initiative(key)
        return key

    def add_to_initiative(self, key):
        new_token: CreatureToken = self._tokens[key]
        order: float = new_token.roll_initiative()
        if order in self._initiative_order and self._initiative_order[order] is not key:
            roll, log_str = self._die.roll()
            order += roll/1000
        self._initiative_order[order] = key

    def get_token_key(self, token: CreatureToken) -> str:
        return [key for key in self._tokens.keys() if self._tokens[key] is token][0]

    def remove_token(self, key: str):
        if key in self._tokens.keys():
            self.remove_from_initiative(key)
            return self._tokens.pop(key)

    def remove_from_initiative(self, key: str):
        if key in self._initiative_order.values():
            position = next((pos for pos, p_key in self._initiative_order.items() if p_key == key), 0.0)
            self._initiative_order.pop(position)

    def process_turn(self):
        for order in sorted(self._initiative_order.keys(), reverse=True):
            token_key = self._initiative_order[order]
            self._tokens[token_key].take_turn()

    @property
    def initiative_order(self):
        return self._initiative_order

    @property
    def die(self):
        return self._die

    @initiative_order.setter
    def initiative_order(self, value):
        self._initiative_order = value

    @tokens.setter
    def tokens(self, value):
        self._tokens = value
