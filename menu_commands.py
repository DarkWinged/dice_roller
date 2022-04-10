from game_state import GameState


def quit_game(current_game_state: GameState) -> None:
    print('Shutting down game')
    current_game_state.running = False


def open_movement_menu(current_game_state: GameState) -> None:
    current_game_state.menus['selection'].curser = current_game_state.player.position
    current_game_state.menus['main'].pause()
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
    current_game_state.menus['main'].unpause()


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
        current_game_state.renderer.load_entities(current_game_state.turn_tracker.tokens)
        current_game_state.menus['selection'].deactivate()
        current_game_state.menus['main'].unpause()
