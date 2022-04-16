import json
from abc import ABC, abstractmethod

from tcod import Console

from character_sheet import CharacterSheet, StatBlock, Equipment, Armor, Weapon
from character_sheet.enums import AbilityScore, EquipmentSlot
from color import Color
from die import Dice
from game_state import GameState
from map_renderer import MapRenderer
from map_token import CreatureToken
from room import Room
from turn_tracker import TurnTracker


class Loadable(ABC):

    @classmethod
    @abstractmethod
    def encode(cls, obj: any) -> dict[str, any]: pass

    @classmethod
    @abstractmethod
    def decode(cls, encoded: dict[str, any]) -> any: pass


class RoomLoader(Loadable):
    @classmethod
    def encode(cls, obj: Room) -> dict[str, any]:
        rows = obj.stringify().split(sep='\n')
        while '' in rows:
            rows.remove('')
        height = len(rows)
        width = len(rows[0])
        tile_map = []
        for row in range(height):
            column = []
            for tile in range(width):
                column.append(f'{rows[row][tile]}')
            tile_map.append(column.copy())

        return {
            'seed': obj.seed,
            'tile_set': obj.tile_set,
            'tile_map': tile_map
        }

    @classmethod
    def decode(cls, encoded: dict[str, any]) -> Room:
        return Room.new(encoded['seed'], encoded['tile_set'], encoded['tile_map'])


class TurnTrackerLoader(Loadable):
    @classmethod
    def encode(cls, obj: TurnTracker) -> dict[str, any]:
        tokens = {}
        for token in obj.tokens.keys():
            tokens[token] = CreatureTokenLoader.encode(obj.tokens[token])
        return {
            'tokens': obj.tokens,
            'initiative_order': obj.initiative_order,
            'seed': obj.die.seed
        }

    @classmethod
    def decode(cls, encoded: dict[str, any]) -> TurnTracker:
        tracker: TurnTracker = TurnTracker(encoded['seed'])
        tokens = {}
        for token in encoded['tokens'].keys():
            tokens[token] = CreatureTokenLoader.decode(encoded['tokens'][token])
        tracker.initiative_order = encoded['initiative_order']
        tracker.tokens = tokens
        return tracker


class RaceLoader(Loadable):
    @classmethod
    def encode(cls, obj: dict[str, any]) -> dict[str, any]:
        encoding = {}
        for key in obj.keys():
            if key == 'ability_mod':
                encoding[key] = {}
                for ability_score in obj[key].keys():
                    encoding[key][ability_score.name] = obj[key][ability_score]
            else:
                encoding[key] = obj[key]
        return encoding

    @classmethod
    def decode(cls, encoded: dict[str, any]) -> dict[str, any]:
        decoding = {}
        for key in encoded.keys():
            if key == 'ability_mod':
                decoding[key] = {}
                for ability_score in encoded[key].keys():
                    decoding[key][decode_ability_score(ability_score)] = encoded[key][ability_score]
            else:
                decoding[key] = encoded[key]
        return decoding


class StatBlockLoader(Loadable):
    @classmethod
    def encode(cls, obj: StatBlock) -> dict[str, any]:
        encoding = {}
        for key in obj.ability_scores.keys():
            encoding[key.name] = obj.ability_scores[key]
        return encoding

    @classmethod
    def decode(cls, encoded: dict[str, any]) -> StatBlock:
        ability_scores = {}
        for key in encoded.keys():
            ability_scores[decode_ability_score(key)] = encoded[key]
        return StatBlock(ability_scores)


class EquipmentLoader(Loadable):
    @classmethod
    def encode(cls, obj: Equipment) -> dict[str, any]:
        if isinstance(obj, Armor):
            return {
                'type': 'Armor',
                'name': obj.name,
                'equipment_slot': obj.equipment_slot.name,
                'armor_class': obj.armor_class,
                'effects': obj.effects,
                'restrictions': obj.restrictions
            }
        elif isinstance(obj, Weapon):
            return {
                'type': 'Weapon',
                'name': obj.name,
                'equipment_slot': obj.equipment_slot.name,
                'roll_type': f'{obj.die_type}{obj.modifier}',
                'damage_type': obj.damage_type,
                'zweihand': obj.zweihand,
                'restrictions': obj.restrictions
            }

    @classmethod
    def decode(cls, encoded: dict[str, any]) -> Equipment:
        if encoded['type'] == 'Armor':
            return Armor(
                encoded['name'],
                decode_equipment_slot(encoded['equipment_slot']),
                encoded['armor_class'],
                encoded['effects'],
                encoded['restrictions']
            )
        elif encoded['type'] == 'Weapon':
            return Weapon(
                encoded['name'],
                decode_equipment_slot(encoded['equipment_slot']),
                (encoded['roll_type'], encoded['damage_type']),
                encoded['zweihand'],
                encoded['restrictions']
            )


class CharacterSheetLoader(Loadable):
    @classmethod
    def encode(cls, obj: CharacterSheet) -> dict[str, any]:
        dice = {}
        for die in obj.dice.keys():
            dice[die] = obj.dice[die].seed
        equipment = {}
        for key in obj.equipment.keys():
            equipment[key.name] = EquipmentLoader.encode(obj.equipment[key])
        inventory = []
        for item in obj.inventory:
            inventory.append(EquipmentLoader.encode(item))

        return {
           'ability_scores': StatBlockLoader.encode(obj.ability_scores),
           'race': RaceLoader.encode(obj.race),
           'role': obj.role,
           'dice': dice,
           'equipment': equipment,
           'inventory': inventory,
           'hp': obj.hp,
           'max_hp': obj.max_hp
        }

    @classmethod
    def decode(cls, encoded: dict[str, any]) -> CharacterSheet:
        sheet = CharacterSheet(
            StatBlockLoader.decode(encoded['ability_scores']),
            RaceLoader.decode(encoded['race']),
            encoded['role']
        )
        dice = {}
        for die in encoded['dice'].keys():
            dice[die] = Dice(die, encoded['dice'][die])
        equipment = {}
        for key in encoded['equipment'].keys():
            if encoded['equipment'][key] is not None:
                equipment[decode_equipment_slot(key)] = EquipmentLoader.decode(encoded['equipment'][key])
            else:
                equipment[decode_equipment_slot(key)] = None
        inventory = []
        for item in encoded['inventory']:
            if item is not None:
                inventory.append(EquipmentLoader.decode(item))
        sheet.dice = dice
        sheet.equipment = equipment
        sheet.inventory = inventory
        return sheet


class CreatureTokenLoader(Loadable):
    @classmethod
    def encode(cls, obj: CreatureToken) -> dict[str, any]:
        return {
            'name': obj.name,
            'position': obj.position,
            'sheet':  CharacterSheetLoader.encode(obj.sheet)
        }

    @classmethod
    def decode(cls, encoded: dict[str, any]) -> CreatureToken:
        return CreatureToken(
            encoded['name'],
            tuple(encoded['position']),
            CharacterSheetLoader.decode(encoded['sheet'])
        )


class GameStateLoader(Loadable):
    @classmethod
    def encode(cls, obj: GameState) -> dict[str, any]:
        rooms = []
        for room in obj.rooms:
            rooms.append(RoomLoader.encode(room))
        temp_tokens = obj.turn_tracker.tokens.copy()
        temp_turn_order = obj.turn_tracker.initiative_order.copy()
        obj.turn_tracker.remove_token(obj.turn_tracker.get_token_key(obj.player))
        jdict = {
            'fps': obj.fps,
            'fps_uncapped': obj.fps_uncapped,
            'rooms': rooms,
            'current_room': obj.current_room,
            'turn_tracker': TurnTrackerLoader.encode(obj.turn_tracker),
            'player': CreatureTokenLoader.encode(obj.player),
        }
        obj.turn_tracker.initiative_order = temp_turn_order
        obj.turn_tracker.tokens = temp_tokens
        return jdict

    @classmethod
    def decode(cls, encoded: dict[str, any], /, *, console: Console) -> any:
        turn_tracker: TurnTracker = TurnTrackerLoader.decode(encoded['turn_tracker'])
        player = CreatureTokenLoader.decode(encoded['player'])
        turn_tracker.add_token(player)
        rooms = []
        for room in encoded['rooms']:
            rooms.append(RoomLoader.decode(room))

        renderer = MapRenderer((0, 0), (20, 20))
        wall_fg, wall_bg = Color(0.1, 0.2, 0.3), Color(0.1, 0.1, 0.2)
        renderer.add_rule('W', 'fftt', renderer.pipe_symbols[0], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'tfft', renderer.pipe_symbols[1], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'ttff', renderer.pipe_symbols[2], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'fttf', renderer.pipe_symbols[3], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'ttft', renderer.pipe_symbols[4], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'fttt', renderer.pipe_symbols[5], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'tftt', renderer.pipe_symbols[6], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'tttf', renderer.pipe_symbols[7], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'tttt', renderer.pipe_symbols[8], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'ftft', renderer.pipe_symbols[9], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'ftff', renderer.pipe_symbols[9], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'ffft', renderer.pipe_symbols[9], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'tftf', renderer.pipe_symbols[10], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'tfff', renderer.pipe_symbols[10], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('W', 'fftf', renderer.pipe_symbols[10], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('F', 'a', renderer.block_symbols[2], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('R', 'a', renderer.block_symbols[0], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('U', 'a', renderer.block_symbols[4], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('D', 'a', renderer.block_symbols[3], foreground=wall_fg, background=wall_bg)
        renderer.add_rule('E', 'a', ' ', foreground=wall_fg, background=wall_bg)
        renderer.position = (17, 1)

        game_state = GameState(
            True,
            False,
            encoded['fps'],
            encoded['fps_uncapped'],
            {},
            {},
            rooms,
            encoded['current_room'],
            turn_tracker,
            player,
            renderer,
            console,
            {}
        )

        return game_state


def decode_ability_score(score: str) -> AbilityScore:
    match score:
        case "STR":
            return AbilityScore.STR
        case "CON":
            return AbilityScore.CON
        case "DEX":
            return AbilityScore.DEX
        case "INT":
            return AbilityScore.INT
        case "WIS":
            return AbilityScore.WIS
        case "CHA":
            return AbilityScore.CHA


def decode_equipment_slot(slot: str) -> EquipmentSlot:
    match slot:
        case 'head':
            return EquipmentSlot.head
        case 'neck':
            return EquipmentSlot.neck
        case 'body':
            return EquipmentSlot.body
        case 'back':
            return EquipmentSlot.back
        case 'arms':
            return EquipmentSlot.arms
        case 'hands':
            return EquipmentSlot.hands
        case 'hand_l':
            return EquipmentSlot.hand_l
        case 'fingers_l':
            return EquipmentSlot.fingers_l
        case 'hand_r':
            return EquipmentSlot.hand_r
        case 'fingers_r':
            return EquipmentSlot.fingers_r
        case 'waist':
            return EquipmentSlot.waist
        case 'legs':
            return EquipmentSlot.legs
        case 'feet':
            return EquipmentSlot.feet


def load_races():
    races_to_return = {}
    with open('./assets/races.json', 'r') as file:
        races = json.JSONDecoder().decode(file.read())
        for race_name in races.keys():
            races_to_return[race_name] = {}
            races_to_return[race_name]['name'] = races[race_name]['name']
            races_to_return[race_name]['ability_mod'] = {}
            for score in races[race_name]['ability_mod'].keys():
                races_to_return[race_name]['ability_mod'][decode_ability_score(score)] =\
                    races[race_name]['ability_mod'][score]
    return races_to_return