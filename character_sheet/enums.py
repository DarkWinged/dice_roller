import enum


class ResistanceLevel(enum.Enum):
    bane = 'bane'
    weakness = 'weakness'
    normal = 'normal'
    resistant = 'resistant'
    immune = 'immune'


class AbilityScore(enum.Enum):
    STR = 'strength'
    CON = 'constitution'
    DEX = 'dexterity'
    INT = 'intelligence'
    WIS = 'wisdom'
    CHA = 'charisma'


def ability_score_iterator() -> list[str]:
    return [
            AbilityScore.STR,
            AbilityScore.CON,
            AbilityScore.DEX,
            AbilityScore.INT,
            AbilityScore.WIS,
            AbilityScore.CHA
            ]


class EquipmentSlot(enum.IntEnum):
    head = 0
    neck = 1
    body = 2
    back = 3
    arms = 4
    hands = 5
    hand_l = 6
    fingers_l = 7
    hand_r = 8
    fingers_r = 9
    waist = 10
    legs = 11
    feet = 12


def equipment_slot_iterator() -> list[int]:
    return [
            EquipmentSlot.head,
            EquipmentSlot.neck,
            EquipmentSlot.body,
            EquipmentSlot.back,
            EquipmentSlot.arms,
            EquipmentSlot.hands,
            EquipmentSlot.hand_l,
            EquipmentSlot.fingers_l,
            EquipmentSlot.hand_r,
            EquipmentSlot.fingers_r,
            EquipmentSlot.waist,
            EquipmentSlot.legs,
            EquipmentSlot.feet
            ]
