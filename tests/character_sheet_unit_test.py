import math

from character_sheet import CharacterSheet, ResistanceLevel
from character_sheet.stat_block import AbilityScore, ability_score_iterator, StatBlock
from character_sheet.equipment import Weapon, EquipmentSlot, Armor


def test_base_armor_class():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    scores[AbilityScore.DEX] += 4
    race = {'ability_mod': race_modifiers}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')

    assert fighter.armor_class == 12


def test_natural_armor():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {'ability_mod': race_modifiers, 'natural_ac': 2}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')

    assert fighter.armor_class == 12


def test_equip_helmet():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {'ability_mod': race_modifiers}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')
    helmet = Armor('Iron Helm', EquipmentSlot.head, 2)

    fighter.equip(helmet)

    assert fighter.armor_class == 12


def test_equip_hat():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {'ability_mod': race_modifiers}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')
    helmet = Armor('Iron Helm', EquipmentSlot.head, 2)
    hat = Armor('Fancy Hat', EquipmentSlot.head, 0)

    fighter.equip(helmet)
    fighter.equip(hat)

    assert fighter.armor_class == 10
    assert helmet in fighter.inventory
    assert hat not in fighter.inventory


def test_equip_armor_set():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {'ability_mod': race_modifiers}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')
    helmet = Armor('Iron Helm', EquipmentSlot.head, 2)
    armor = Armor('Iron Scalemail', EquipmentSlot.body, 4)

    fighter.equip(helmet)
    fighter.equip(armor)

    assert fighter.armor_class == 16


def test_unarmed():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {'ability_mod': race_modifiers, 'natural_weapon': ('1d6', 'slashing')}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')

    assert fighter.dice['1d6'].die_type == '1d6'


def test_equip_weapon():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {'ability_mod': race_modifiers}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')
    sword = Weapon('Iron Sword', EquipmentSlot.hand_r, ('1d8', 'slashing'), False)
    dagger = Weapon('Iron Dagger', EquipmentSlot.hand_r, ('1d4', 'piercing'), False)
    offhand = True

    fighter.equip(sword)
    fighter.equip(dagger, offhand)

    assert fighter.equipment[EquipmentSlot.hand_r].equipment_name == 'Iron Sword'
    assert fighter.equipment[EquipmentSlot.hand_l].equipment_name == 'Iron Dagger'


def test_equip_zweihand():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {'ability_mod': race_modifiers}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')
    sword = Weapon('Iron Sword', EquipmentSlot.hand_r, ('1d8', 'slashing'), False)
    dagger = Weapon('Iron Dagger', EquipmentSlot.hand_r, ('1d4', 'piercing'), False)
    zweihander = Weapon('Iron Zweihander', EquipmentSlot.hand_r, ('1d12', 'slashing'), True)
    offhand = True

    fighter.equip(sword)
    fighter.equip(dagger, offhand)
    fighter.equip(zweihander)

    assert fighter.equipment[EquipmentSlot.hand_r].equipment_name == 'Iron Zweihander'
    assert fighter.equipment[EquipmentSlot.hand_l] is None


def test_equip_offhand():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {'ability_mod': race_modifiers}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')
    dagger = Weapon('Iron Dagger', EquipmentSlot.hand_r, ('1d4', 'piercing'), False)
    zweihander = Weapon('Iron Zweihander', EquipmentSlot.hand_r, ('1d12', 'slashing'), True)
    offhand = True

    fighter.equip(zweihander)
    fighter.equip(dagger, offhand)

    assert fighter.equipment[EquipmentSlot.hand_r] is None
    assert fighter.equipment[EquipmentSlot.hand_l].equipment_name == 'Iron Dagger'


def test_attack():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race_modifiers[AbilityScore.STR] += 4
    race = {'ability_mod': race_modifiers}
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')
    rouge = CharacterSheet(StatBlock(scores), race, 'rouge')
    damage, damage_type = None, None

    hit, roll = mock_attack(fighter.ability_scores.str_mod, rouge.armor_class)
    if hit:
        damage, damage_type = fighter.roll_damage()
        rouge.take_damage(damage, damage_type)

    assert roll > rouge.armor_class
    assert rouge.hp == rouge.max_hp - damage


def mock_attack(fighter_attack: int, rouge_ac: int) -> (bool, int):
    return 10 + fighter_attack > rouge_ac, 10 + fighter_attack


def test_resistance():
    scores = {}
    race_modifiers = {}
    for score in ability_score_iterator():
        scores[score] = 10
        race_modifiers[score] = 0
    race = {
            'ability_mod': race_modifiers,
            'resistances': {'slashing': ResistanceLevel.resistant}
            }
    fighter = CharacterSheet(StatBlock(scores), race, 'fighter')
    rouge = CharacterSheet(StatBlock(scores), race, 'rouge')
    sword = Weapon('Iron Sword', EquipmentSlot.hand_r, ('1d8+1', 'slashing'), False)
    damage, damage_type = None, None

    fighter.equip(sword)
    hit, roll = mock_attack(fighter.ability_scores.str_mod + 1, rouge.armor_class)
    if hit:
        damage, damage_type = fighter.roll_damage(EquipmentSlot.hand_r)
        rouge.take_damage(damage, damage_type)
        damage = math.floor(damage / 2)
        if damage < 1:
            damage = 1

    assert damage_type is 'slashing'
    assert rouge.hp == rouge.max_hp - damage

# robert martin: clean code
