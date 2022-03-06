from character_sheet.enums import ability_score_iterator, AbilityScore
import math


def get_mod(score: int) -> int:
    return math.floor((score - 10) / 2)


class StatBlock:
    def __init__(self, ability_scores: dict[str, int]):
        self.ability_scores: dict[str: int] = {}
        for key, score in enumerate(ability_scores):
            self.ability_scores[score] = ability_scores[score]

    def apply_race_ability_scores(self, race_mods: dict[str, int]):
        for key in ability_score_iterator():
            self.ability_scores[key] += race_mods[key]

    @property
    def str_score(self) -> int:
        return self.ability_scores[AbilityScore.STR]

    @property
    def str_mod(self):
        return get_mod(self.ability_scores[AbilityScore.STR])

    @property
    def dex_score(self) -> int:
        return self.ability_scores[AbilityScore.DEX]

    @property
    def dex_mod(self):
        return get_mod(self.ability_scores[AbilityScore.DEX])

    @property
    def con_score(self) -> int:
        return self.ability_scores[AbilityScore.CON]

    @property
    def con_mod(self):
        return get_mod(self.ability_scores[AbilityScore.CON])

    @property
    def int_score(self) -> int:
        return self.ability_scores[AbilityScore.INT]

    @property
    def int_mod(self):
        return get_mod(self.ability_scores[AbilityScore.INT])

    @property
    def wis_score(self) -> int:
        return self.ability_scores[AbilityScore.WIS]

    @property
    def wis_mod(self):
        return get_mod(self.ability_scores[AbilityScore.WIS])

    @property
    def cha_score(self) -> int:
        return self.ability_scores[AbilityScore.CHA]

    @property
    def cha_mod(self):
        return get_mod(self.ability_scores[AbilityScore.CHA])
