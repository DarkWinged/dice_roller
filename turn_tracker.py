from map_token import CreatureToken


class TurnTracker:
    def __init__(self):
        self._tokens: list[CreatureToken] = []

    def sort_tokens(self):
        self._tokens.sort()