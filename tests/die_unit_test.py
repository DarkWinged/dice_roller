from die import Advantage
from die import Dice


def main():
    test_dice()
    test_new_dice()
    test_invalid_dice()
    test_roll_in_range()
    test_roll_reproduction()
    test_advantageous_roll()
    test_disadvantageous_roll()


def test_dice():
    die_type = '1d6'
    new_die = Dice(die_type)
    assert new_die.is_valid()


def test_new_dice():
    number = 1
    size = 8
    new_die = Dice.new(number, size)
    assert new_die.is_valid()


def test_invalid_dice():
    die_type = '1d-12'
    new_die = Dice(die_type)
    assert not new_die.is_valid()


def test_roll_in_range():
    new_die = Dice('1d20')
    for roll in range(1000):
        result = new_die.roll()
        assert 1 <= result <= new_die.size


def test_roll_reproduction():
    die_1 = Dice('1d4', 1234)
    die_2 = Dice.new(die_1.number, die_1.size, die_1._seed)
    for roll in range(1000):
        assert die_1.roll() == die_2.roll()


def test_advantageous_roll():
    die_1 = Dice('1d10', 5678)
    die_2 = Dice.new(die_1.number, die_1.size, die_1._seed)
    for roll in range(1000):
        roll_1, roll_2 = die_2.roll(), die_2.roll()
        assert die_1.roll_advantage(Advantage.adv) == max(roll_1, roll_2)


def test_disadvantageous_roll():
    die_1 = Dice('1d100', 9012)
    die_2 = Dice.new(die_1.number, die_1.size, die_1._seed)
    for roll in range(1000):
        roll_1, roll_2 = die_2.roll(), die_2.roll()
        assert die_1.roll_advantage(Advantage.dis) == min(roll_1, roll_2)


def test_modified_roll():
    die_1 = Dice('1d20', 3456)
    die_2 = Dice('1d20', 3456)
    for roll in range(1000):
        assert die_1.roll(modifier=1) == die_2.roll(modifier=1)


if __name__ == '__main__':
    main()
