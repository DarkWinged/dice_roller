from character_sheet.enums import EquipmentSlot
from abc import ABC, abstractmethod


class Equipment(ABC):

    @property
    @abstractmethod
    def equipment_name(self) -> str: pass

    @property
    @abstractmethod
    def equipment_slot(self) -> EquipmentSlot: pass

    @property
    @abstractmethod
    def restrictions(self) -> list[str]: pass


class Armor(Equipment):
    def __init__(self, name: str, equipment_slot: EquipmentSlot, armor_class: int,
                 effects: list[str] = None, restrictions: list[str] = None):
        self._name = name
        self._equipment_slot = equipment_slot
        self._armor_class = armor_class
        self._effects = effects
        self._restrictions = restrictions

    @property
    def equipment_name(self) -> str:
        return self._name

    @property
    def equipment_slot(self) -> EquipmentSlot:
        return self._equipment_slot

    @property
    def armor_class(self) -> int:
        return self._armor_class

    @property
    def effects(self) -> list[str]:
        return self._effects

    @property
    def restrictions(self) -> list[str]:
        return self._restrictions

    @property
    def name(self):
        return self._name


class Weapon(Equipment):
    def __init__(self, name: str, equipment_slot: EquipmentSlot, roll_type: tuple[str, str], zweihand: bool,
                 restrictions: list[str] = None):
        roll_type, damage_type = roll_type
        self._name = name
        self._equipment_slot = equipment_slot
        if '+' in roll_type:
            self._die_type, self._modifier = roll_type.split(sep='+')
        elif '-' in roll_type:
            self._die_type, self._modifier = roll_type.split(sep='-')
        elif roll_type is not None:
            self._die_type, self._modifier = roll_type, 0
        else:
            self._die_type, self._modifier = None, None
        self._damage_type = damage_type
        self._zweihand = zweihand
        self._restrictions = restrictions

    @property
    def equipment_name(self) -> str:
        return self._name

    @property
    def equipment_slot(self) -> EquipmentSlot:
        return self._equipment_slot

    @property
    def die_type(self) -> str:
        return self._die_type

    @property
    def modifier(self) -> int:
        return int(self._modifier)

    @property
    def damage_type(self) -> str:
        return self._damage_type

    @property
    def zweihand(self) -> bool:
        return self._zweihand

    @property
    def restrictions(self) -> list[str]:
        return self._restrictions
