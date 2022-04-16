from dataclasses import dataclass

from tcod import Console

from gui_element import GuiElement
from map_renderer import MapRenderer
from map_token import CreatureToken
from menus import Menu
from room import Room
from turn_tracker import TurnTracker


@dataclass
class GameState:
    running: bool
    paused: bool
    fps: int
    fps_uncapped: bool
    menus: dict[str, Menu]
    gui_elements: dict[str, GuiElement]
    rooms: list[Room]
    current_room: int
    turn_tracker: TurnTracker
    player: CreatureToken
    renderer: MapRenderer
    console: Console
    data_table: dict[str: any]

