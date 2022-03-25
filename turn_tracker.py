from die import Dice
from map_token import CreatureToken


class TurnTracker:
    def __init__(self, seed: int):
        self._tokens: dict[str, CreatureToken] = {}
        self._initiative_order = dict[float, str] = {}
        self._die = Dice('1d10', seed)

    def add_token(self, new_token: CreatureToken) -> str:
        key = ''
        if new_token not in self._tokens.values():
            for iterations in range(16):
                roll = self._die.roll()
                key = f'{key}{roll[0]-1}'
            self._tokens[key] = new_token
            self.add_to_initiative(key)
        return key

    def add_to_initiative(self, key):
        order: float = self._tokens[key].roll_initaiave()
        if order in self._initiative_order and self._initiative_order[order] is not key:
            roll, log_str = self._die.roll()
            order += roll/1000
        self._initiative_order[order] = key

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
