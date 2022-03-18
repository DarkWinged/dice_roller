import pygame
import tcod
from pygame.constants import KEYDOWN, K_ESCAPE

from map_token import CreatureToken
from room import Room


def game_init() -> pygame.display:
    pygame.init()
    return pygame.display.set_mode([500, 500])


def game_loop(screen: pygame.display):
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)
        pygame.display.flip()

    pygame.quit()


def main():

    screen_width = 80
    screen_height = 50

    tile_set = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tile_set,
        title="Yet Another Roguelike Tutorial",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        running = True
        menu = Menu((1, 1), {'Move': None, 'Inventory': None, 'Exit': SystemExit})
        while running:

            context.present(root_console)
            menu.render(root_console)

            tile_set = {
                'E': {'icon': -1, 'description': 'An empty void...'},
                'F': {'icon': 0, 'description': 'A patch of smooth stone floor.'},
                'W': {'icon': 1, 'passable': False, 'description': 'A solid brick wall.'},
                'R': {'icon': 2, 'movement_cost': 2, 'description': 'A pile of rubble littering the floor.'},
                'U': {'icon': 3, 'description': 'A staircase leading up to the surface.'},
                'D': {'icon': 4, 'description': 'A staircase leading down deeper into the dungeon.'}
            }
            tile_map = [
                ['W', 'W', 'W', 'W', 'W', 'W', 'W'],
                ['W', 'D', 'W', 'U', 'R', 'F', 'W'],
                ['W', 'F', 'W', 'F', 'R', 'F', 'W'],
                ['W', 'F', 'W', 'F', 'R', 'F', 'W'],
                ['W', 'F', 'F', 'F', 'F', 'F', 'W'],
                ['W', 'F', 'F', 'F', 'F', 'F', 'W'],
                ['W', 'W', 'W', 'W', 'W', 'W', 'W']
            ]
            test_room = Room.new(5678, tile_set, tile_map)
            player_start = [position for position in test_room.tiles.keys() if test_room.tiles[position].icon == 3][0]
            player = CreatureToken('player_name', player_start, {})
            test_room.add_token(player)
            root_console.print(x=15, y=5, string=f"{test_room}")

            for event in tcod.event.wait():
                context.convert_event(event)  # Add tile coordinates to mouse events.
                match event:
                    case tcod.event.Quit():
                        raise SystemExit()
                    case tcod.event.KeyDown():
                        match event.sym:
                            case tcod.event.K_UP:
                                menu.curser_up()
                            case tcod.event.K_DOWN:
                                menu.curser_down()
                            case tcod.event.K_SPACE:
                                print(menu.menu_options[menu.curser_key])
                                menu.select(player, test_room)
                            case tcod.event.K_ESCAPE:
                                raise SystemExit()

                        print(f"KeyDown: {event}")
                    case tcod.event.MouseButtonDown():
                        print(f"MouseButtonDown: {event}")
                    case tcod.event.MouseMotion():
                        print(f"MouseMotion: {event}")
                    case tcod.event.Event() as event:
                        print(event)  # Show any unhandled events.


class Menu:
    def __init__(self, position: tuple[int, int], options: dict[str, callable(None)]):
        self.position = position
        self.menu_options = options
        self.curser = 0

    def curser_up(self):
        self.curser -= 1
        if self.curser < 0:
            self.curser = len(self.menu_options) - 1

    def curser_down(self):
        self.curser += 1
        if self.curser >= len(self.menu_options):
            self.curser = 0

    def render(self, console: tcod.Console):
        console.clear()
        console.print(x=self.position[0], y=self.position[1], string="MENU")
        for item, menu_item in enumerate(self.menu_options.keys()):
            if item == self.curser:
                console.print(x=self.position[0], y=self.position[1] + item + 1, string=menu_item, fg=(0, 255, 0))
            else:
                console.print(x=self.position[0], y=self.position[1] + item + 1, string=menu_item)

    @property
    def curser_key(self):
        return [key for index, key in enumerate(self.menu_options.keys()) if index == self.curser][0]

    def select(self, current_token: CreatureToken, current_room: Room):
        curser_key = self.curser_key
        if self.menu_options[curser_key] is SystemExit:
            raise SystemExit()
        elif self.menu_options[curser_key] is not None:
            self.menu_options[curser_key](current_token, current_room)


if __name__ == '__main__':
    main()
    # game_loop(game_init())
