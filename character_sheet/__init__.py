from character_sheet.enums import ResistanceLevel, EquipmentSlot
from character_sheet.equipment import Armor, Equipment, Weapon
from character_sheet.stat_block import StatBlock
from typing import Dict
from die import Dice
import math


class CharacterSheet:
    def __init__(self, ability_scores: StatBlock, race, role):
        self.ability_scores = ability_scores
        self.race = race
        self.role = role
        if 'ability_mod' in race:
            self.ability_scores.apply_race_ability_scores(self.race['ability_mod'])
        self.dice = {'1d20': Dice('1d20')}
        if 'natural_weapon' in self.race:
            die_type, damage_type = race['natural_weapon']
            self.add_dice(die_type)
        else:
            die_type, damage_type = '1d4', 'bludgeoning'
            self.race['natural_weapon'] = die_type, damage_type
            self.add_dice(die_type)
        self.equipment: Dict[EquipmentSlot, Equipment or None] = {EquipmentSlot.head: None}
        for slot in enums.equipment_slot_iterator():
            self.equipment[slot] = None
        self.inventory = []
        self._max_hp = 10 + self.ability_scores.con_mod
        self._hp = self._max_hp

    @property
    def movement_speed(self) -> int:
        if 'movement_speed' in self.race:
            return self.race['movement_speed']
        else:
            return 5

    @property
    def max_hp(self):
        return self._max_hp

    @property
    def hp(self):
        return self._hp

    @property
    def armor_class(self):
        if 'natural_ac' in self.race:
            natural_ac = self.race['natural_ac']
        else:
            natural_ac = 0
        return 10 + self.ability_scores.dex_mod + natural_ac + self.get_equipment_buff('armor_class')

    def get_equipment_buff(self, buff: str) -> int:
        match buff:
            case 'armor_class':
                result: int = 0
                equipment_local: list[Armor] = [self.equipment[key] for key in self.equipment
                                                if type(self.equipment[key]) is Armor]
                for item in equipment_local:
                    result += item.armor_class
                return result

    def add_dice(self, die_type: str):
        if die_type not in self.dice:
            self.dice[die_type] = Dice(die_type)

    def equip(self, item: Equipment, offhand_weapon: bool = False):
        if type(item) is Weapon:
            weapon: Weapon = item
            self.equip_weapon(weapon, offhand_weapon)
        else:
            if self.equipment[item.equipment_slot] is None:
                self.equipment[item.equipment_slot] = item
            else:
                self.unequip(item.equipment_slot, item)

            if item in self.inventory:
                self.inventory.remove(item)

    def equip_weapon(self, weapon: Weapon, offhand_weapon: bool = False):
        if offhand_weapon and not weapon.zweihand:
            slot = EquipmentSlot.hand_l
        else:
            slot = weapon.equipment_slot

        if self.equipment[EquipmentSlot.hand_r] is not None and slot == EquipmentSlot.hand_l:
            main_hand: Weapon = self.equipment[EquipmentSlot.hand_r]
            if main_hand.zweihand:
                self.unequip(EquipmentSlot.hand_r)

        if self.equipment[slot] is None:
            self.equipment[slot] = weapon
            if weapon.zweihand:
                self.unequip(EquipmentSlot.hand_l)
        else:
            if weapon.zweihand:
                self.unequip(EquipmentSlot.hand_l)
                self.unequip(weapon.equipment_slot, weapon)
            else:
                self.unequip(weapon.equipment_slot, weapon)

        self.add_dice(weapon.die_type)
        if weapon in self.inventory:
            self.inventory.remove(weapon)

    def unequip(self, slot: EquipmentSlot, replacement: Equipment = None):
        self.inventory.append(self.equipment[slot])
        self.equipment[slot] = replacement

    def roll_initiative(self):
        return self.dice['1d20'].roll(modifier=self.ability_scores.dex_mod)

    def attack(self, target_ac: int, weapon_slot: EquipmentSlot = None) -> tuple[bool, int]:
        modifier = self.ability_scores.str_mod
        if (weapon_slot is EquipmentSlot.hand_r or weapon_slot is EquipmentSlot.hand_l) and \
                type(self.equipment[weapon_slot]) is Weapon:
            weapon: Weapon = self.equipment[weapon_slot]
            modifier += weapon.modifier
        roll = self.dice['1d20'].roll(modifier=modifier)
        return roll > target_ac, roll

    def roll_damage(self, weapon_slot: EquipmentSlot = None) -> tuple[int, str]:
        modifier = self.ability_scores.str_mod
        if (weapon_slot is EquipmentSlot.hand_r or weapon_slot is EquipmentSlot.hand_l) and \
                type(self.equipment[weapon_slot]) is Weapon:
            weapon: Weapon = self.equipment[weapon_slot]
            modifier += weapon.modifier
            return self.dice[weapon.die_type].roll(modifier=modifier), weapon.damage_type
        else:
            return self.dice[self.race['natural_weapon'][0]].roll(modifier=modifier), self.race['natural_weapon'][1]

    def take_damage(self, damage: int, damage_type: str):
        if 'resistances' in self.race and damage_type in self.race['resistances']:
            match self.race['resistances'][damage_type]:
                case ResistanceLevel.bane:
                    damage *= 4
                case ResistanceLevel.weakness:
                    damage *= 2
                case ResistanceLevel.normal:
                    damage = damage
                case ResistanceLevel.resistant:
                    damage = math.floor(damage / 2)
                    if damage < 1:
                        damage = 1
                case ResistanceLevel.immune:
                    damage = math.floor(damage / 4)
                    if damage < 1:
                        damage = 1
        self._hp -= damage

    def __str__(self):
        return f'CharacterSheet{self.ability_scores, self.race, self.role, self.dice, self.equipment, self.inventory}, ' \
               f'{self._max_hp, self._hp} '
