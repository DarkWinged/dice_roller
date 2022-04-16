import json
import math
from pathlib import Path
import tcod

from character_creation_menu import AbilityScoreMenu, RaceSelectionMenu
from character_sheet import StatBlock, CharacterSheet
from character_sheet.enums import ability_score_iterator, AbilityScore
from game_state import GameState
from info_tab import InfoTab
from loadable import GameStateLoader, load_races
from map_token import CreatureToken
from menus import TextMenu


def quit_game(current_game_state: GameState) -> None:
    print('Shutting down game')
    current_game_state.running = False


def new_game(current_game_state: GameState) -> None:
    current_game_state.menus['main'].deactivate()
    name_entry_text_box = TextMenu((math.floor((80 - 14)/2), 10), (14, 20), current_game_state.console)
    name_entry_text_box.text = 'Who are you?'
    name_entry_text_box.add_command(current_game_state, name='quit', command=quit_game)
    name_entry_text_box.add_command(current_game_state, name='confirm', command=confirm_name)
    name_entry_text_box.add_command(current_game_state, name='cancel', command=cancel_name)
    current_game_state.menus['character_creation_name_text'] = name_entry_text_box
    current_game_state.menus['character_creation_name_text'].activate()


def confirm_name(name: str, current_game_state: GameState) -> None:
    current_game_state.data_table['character_creation_name'] = name
    current_game_state.menus['character_creation_name_text'].deactivate()

    race_selector = RaceSelectionMenu((math.floor((80 - 14) / 2), 10), (14, 20), current_game_state.console)
    race_selector.add_command(current_game_state, name='quit', command=quit_game, hidden=True)
    race_selector.add_command(
        current_game_state,
        name='cancel',
        command=cancel_race,
        hidden=True,
        override=tcod.event.K_ESCAPE
    )
    for race in current_game_state.data_table['races'].keys():
        race_selector.add_command(
            current_game_state.data_table['races'][race],
            current_game_state,
            name=race,
            command=confirm_race
        )
    current_game_state.menus['character_creation_race_selector'] = race_selector
    current_game_state.menus['character_creation_race_selector'].activate()

    character_creation_text = InfoTab((0, 20), (20, 40), current_game_state.console)
    game_data = character_creation_text.game_data
    game_data.append('character_creation_name')
    character_creation_text.game_data = game_data
    current_game_state.gui_elements['character_creation_text'] = character_creation_text
    current_game_state.gui_elements['character_creation_text'].activate()


def cancel_name(current_game_state: GameState) -> None:
    current_game_state.menus['character_creation_name_text'].deactivate()
    current_game_state.gui_elements['character_creation_text'].deactivate()
    current_game_state.menus['main'].activate()


def confirm_race(race: dict[dict[AbilityScore, int]], current_game_state: GameState) -> None:
    current_game_state.data_table['character_creation_race'] = race
    current_game_state.menus['character_creation_race_selector'].deactivate()

    character_creation_text: InfoTab = current_game_state.gui_elements['character_creation_text']
    game_data = character_creation_text.game_data
    game_data.append('character_creation_race')
    character_creation_text.game_data = game_data
    current_game_state.gui_elements['character_creation_text'] = character_creation_text

    ability_score_entry_table = AbilityScoreMenu((math.floor((80 - 14) / 2), 10), (14, 20), current_game_state.console)
    ability_score_entry_table.add_command(current_game_state, name='quit', command=quit_game)
    ability_score_entry_table.add_command(current_game_state, name='confirm', command=confirm_ability_scores)
    ability_score_entry_table.add_command(current_game_state, name='cancel', command=cancel_ability_scores)

    scores = {}
    for score in ability_score_iterator():
        scores[score] = 8
    ability_score_entry_table.data_table = scores
    ability_score_entry_table.free_points = 27

    current_game_state.menus['character_creation_ability_scores'] = ability_score_entry_table
    current_game_state.menus['character_creation_ability_scores'].activate()


def cancel_race(current_game_state: GameState) -> None:
    current_game_state.menus['character_creation_name_text'].activate()
    current_game_state.menus['character_creation_race_selector'].deactivate()
    new_game(current_game_state)


def confirm_ability_scores(ability_scores: dict[str: int], current_game_state: GameState) -> None:
    current_game_state.menus['character_creation_ability_scores'].deactivate()

    current_game_state.gui_elements['character_creation_text'].deactivate()

    player_name = current_game_state.data_table['character_creation_name']
    player_race = current_game_state.data_table['character_creation_race']

    player_sheet = CharacterSheet(StatBlock(ability_scores), player_race, 'fighter')
    player_start = [position for position in current_game_state.rooms[0].tiles.keys()
                    if current_game_state.rooms[0].tiles[position].icon == 3][0]
    current_game_state.turn_tracker.remove_token(current_game_state.turn_tracker.get_token_key(current_game_state.player))
    current_game_state.player = CreatureToken(player_name, player_start, player_sheet)
    current_game_state.turn_tracker.add_token(current_game_state.player)
    current_game_state.renderer.load_tiles(current_game_state.rooms[0].stringify())
    current_game_state.renderer.load_entities(current_game_state.turn_tracker.tokens.values())

    current_game_state.menus['play'].curser = (0, 0)
    current_game_state.menus['play'].activate()
    current_game_state.renderer.activate()
    del(current_game_state.gui_elements['character_creation_text'])


def cancel_ability_scores(current_game_state: GameState) -> None:
    current_game_state.menus['character_creation_ability_scores'].deactivate()
    current_game_state.gui_elements['character_creation_text'].deactivate()
    new_game(current_game_state)


def load_game(current_game_state: GameState) -> None:
    jdict = {}
    path = Path('./saves/save_game.json')
    if path.is_file():
        with open(path, 'r') as file:
            data = file.read()
            if data is not None and data != '':
                jdict = json.JSONDecoder().decode(data)
    if jdict != {}:
        new_game_state = GameStateLoader.decode(jdict, console=current_game_state.console)
        current_game_state.paused = new_game_state.paused
        current_game_state.fps = new_game_state.fps
        current_game_state.fps_uncapped = new_game_state.fps_uncapped
        current_game_state.rooms = new_game_state.rooms
        current_game_state.current_room = new_game_state.current_room
        current_game_state.turn_tracker = new_game_state.turn_tracker
        current_game_state.player = new_game_state.player

        current_game_state.data_table['races'] = load_races()

        current_game_state.renderer.load_tiles(current_game_state.rooms[0].stringify())
        current_game_state.renderer.load_entities(current_game_state.turn_tracker.tokens.values())

        current_game_state.menus['main'].deactivate()
        current_game_state.menus['selection'].deactivate()
        current_game_state.menus['play'].activate()
        current_game_state.menus['play'].pause()
        current_game_state.menus['pause'].activate()
        current_game_state.renderer.activate()


def save_game(current_game_state: GameState):
    path = Path('./saves/save_game.json')
    with open(path, 'w') as file:
        jdict = json.JSONEncoder().encode(GameStateLoader.encode(current_game_state))
        file.write(jdict)


def launch_map_editor(current_game_state: GameState) -> None: pass


def open_movement_menu(current_game_state: GameState) -> None:
    current_game_state.menus['selection'].curser = current_game_state.player.position
    current_game_state.menus['play'].pause()
    highlighted = current_game_state.rooms[current_game_state.current_room].flood_fill(
        current_game_state.player.position,
        current_game_state.player.speed
    )
    current_game_state.renderer.highlighted_tiles = highlighted
    current_game_state.menus['selection'].activate()


def cancel_selection(current_game_state: GameState) -> None:
    current_game_state.renderer.highlighted_tiles = None
    current_game_state.renderer.curser = None
    current_game_state.menus['selection'].deactivate()
    current_game_state.menus['play'].unpause()


def confirm_selection(current_game_state: GameState) -> None:
    movement_range = current_game_state.rooms[current_game_state.current_room].flood_fill(
        current_game_state.player.position,
        current_game_state.player.speed
    )
    curser = current_game_state.menus['selection'].curser
    target_position = (curser[0] % current_game_state.renderer.width, curser[1] % current_game_state.renderer.height)
    if target_position in movement_range:
        current_game_state.player.position = target_position
        current_game_state.renderer.highlighted_tiles = None
        current_game_state.renderer.curser = None
        current_game_state.renderer.load_entities(current_game_state.turn_tracker.tokens.values())
        current_game_state.menus['selection'].deactivate()
        current_game_state.menus['play'].unpause()


def open_pause_menu(current_game_state: GameState):
    current_game_state.menus['play'].pause()
    current_game_state.menus['pause'].activate()


def return_to_tile(current_game_state: GameState):
    current_game_state.menus['play'].deactivate()
    current_game_state.menus['play'].unpause()
    current_game_state.menus['pause'].deactivate()
    current_game_state.renderer.deactivate()
    current_game_state.menus['main'].activate()


def close_pause_menu(current_game_state: GameState):
    current_game_state.menus['play'].unpause()
    current_game_state.menus['pause'].deactivate()


def open_interaction_menu(current_game_state: GameState): pass


def open_attack_menu(current_game_state: GameState): pass
