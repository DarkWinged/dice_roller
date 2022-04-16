from __future__ import annotations
from die.enums import Advantage
from traceback import print_tb
from sys import exc_info
from typing import List
import random


def roll(rand_gen: random.Random, number: int, size: int) -> int:
    result = 0
    for die in range(number):
        result += rand_gen.randint(1, size)
    return result


def roll_advantage(rand_gen: random.Random, number: int, size: int, advantage: Advantage = None) -> int:
    if advantage is None:
        advantage = Advantage.no
    match advantage:
        case Advantage.no:
            return roll(rand_gen, number, size)
        case Advantage.adv:
            result_a: int = roll(rand_gen, number, size)
            result_b: int = roll(rand_gen, number, size)
            return max(result_a,  result_b)
        case Advantage.dis:
            result_a: int = roll(rand_gen, number, size)
            result_b: int = roll(rand_gen, number, size)
            return min(result_a,  result_b)


def make_verbose(result: int, rolls: List[int]) -> str:
    analysis: str = f'Total:{result}, Rolls:('
    for r in rolls:
        analysis = f'{analysis}{r}, '
    analysis = analysis[0:-2]
    analysis = f'{analysis})'
    return analysis


def roll_verbose(rand_gen: random.Random, number: int, size: int) -> (int, str):
    rolls: List[int] = []
    for die in range(number):
        this_roll = rand_gen.randint(1, size)
        rolls.append(this_roll)
    result = sum(rolls)
    return result, make_verbose(result, rolls)


def roll_advantage_verbose(rand_gen: random.Random, number: int, size: int, advantage: Advantage = None)\
        -> (int, str):
    if advantage is None:
        advantage = Advantage.no
    match advantage:
        case Advantage.no:
            return roll_verbose(rand_gen, number, size)
        case Advantage.adv:
            result_a, verbose_a = roll_verbose(rand_gen, number, size)
            result_b, verbose_b = roll_verbose(rand_gen, number, size)
            analysis = f'First roll:{verbose_a}\nSecond roll:{verbose_b}\n'
            result = max(result_a,  result_b)
            return result, f'{analysis}Advantage: {result}'
        case Advantage.dis:
            result_a, verbose_a = roll_verbose(rand_gen, number, size)
            result_b, verbose_b = roll_verbose(rand_gen, number, size)
            analysis = f'First roll:{verbose_a}\nSecond roll:{verbose_b}\n'
            result = min(result_a,  result_b)
            return result, f'{analysis}Disadvantage: {result}'


class Dice:
    def __init__(self, die_type: str, seed: int = None):
        try:
            self._number, self._size = Dice.__parse_die_type__(die_type)
        except ValueError as error:
            exc_type, exc_value, exc_traceback = exc_info()
            print_tb(exc_traceback)
            print(error)
            self._number, self._size = None, None
        if seed is None:
            seed = random.randint(1, 100000)
        self._seed = seed
        self.rand_gen = random.Random(self._seed)
        self._die_type = die_type

    @classmethod
    def new(cls, number: int, size: int, seed: int = None) -> Dice:
        return cls(f'{number}d{size}', seed)

    @classmethod
    def __parse_die_type__(cls, new_dice_type: str) -> (int, int):
        number_size = new_dice_type.split(sep='d')
        number = int(number_size[0])
        if number < 1:
            raise ValueError(f'\nNumber of dice is below the minimum of 1: {number}')
        size = int(number_size[1])
        if size < 2:
            raise ValueError(f'\nSize of dice is below the minimum of 2: {size}')
        return number, size

    def __str__(self):
        return f'Dice(die_type:{self.die_type}, seed:{self._seed})'

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def die_type(self) -> str:
        return self._die_type

    @property
    def number(self) -> int:
        return self._number

    @property
    def size(self) -> int:
        return self._size

    def is_valid(self) -> bool:
        if self.size is None or self.number is None or self.die_type is None or self.rand_gen is None:
            return False
        else:
            return True

    def roll(self, *, verbose: bool = None, modifier: int = None) -> (int, str):
        if verbose:
            result, verbose_result = roll_verbose(self.rand_gen, self.number, self.size)
            if modifier:
                result += modifier
                verbose_result = f'{verbose_result}. Modifier: {modifier}'
            return result, verbose_result
        else:
            if modifier:
                return modifier + roll(self.rand_gen, self.number, self.size)
            return roll(self.rand_gen, self.number, self.size), ''

    def roll_advantage(self, *, advantage: Advantage = None, verbose: bool = None, modifier: int = None) -> (int, str):
        if advantage is None:
            advantage = Advantage.no
        if verbose:
            result, verbose_result = roll_advantage_verbose(self.rand_gen, self.number, self.size, advantage)
            if modifier:
                result += modifier
                verbose_result = f'{verbose_result}. Modifier: {modifier}'
            return result, verbose_result
        else:
            if modifier:
                return modifier + roll_advantage(self.rand_gen, self.number, self.size, advantage)
            else:
                return roll_advantage(self.rand_gen, self.number, self.size, advantage), ''
