from __future__ import annotations

from controllers.game_controller import GameController
from models.game_state import GameState
from models.player import Player
from models.world import World
from views.console_view import ConsoleView


def main() -> None:
    # Initialize compact world and player
    world = World.default_small()
    player = Player(pos=(1, 1))  # (1,1) is guaranteed to be a floor in both defaults
    state = GameState(world=world, player=player)

    view = ConsoleView()
    controller = GameController()

    # Main loop
    while not state.is_over:
        view.render(state)
        try:
            cmd = input("> ")
        except (EOFError, KeyboardInterrupt):
            cmd = "quit"
        controller.handle(cmd, state)

    # final screen
    view.render(state)
    if state.did_win:
        print("\nYou escaped the dungeon—nice work!")
    print("\nThanks for playing!")


if __name__ == "__main__":
    main()