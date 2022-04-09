from dataclasses import dataclass

from tcod import Console

from map_renderer import MapRenderer
from map_token import CreatureToken
from menu import Menu
from room import Room
from turn_tracker import TurnTracker


@dataclass
class GameState:
    running: bool
    fps: int
    fps_uncapped: bool
    menus: dict[str, Menu]
    rooms: list[Room]
    current_room: int
    turn_tracker: TurnTracker
    player: CreatureToken
    renderer: MapRenderer
    console: Console
