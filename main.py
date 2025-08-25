from controllers.game_controller import GameController
from models.game_state import GameState
from models.player import Player
from models.world import World
from views.console_view import ConsoleView


def main() -> None:
    # Initialize world and player
    world = World.default()
    player = Player(pos=(1, 1))  # make sure (1,1) is floor in the map
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
    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
