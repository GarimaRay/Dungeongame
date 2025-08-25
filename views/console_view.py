import os
from models.game_state import GameState


class ConsoleView:
    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def render(self, state: GameState) -> None:
        self.clear()
        print("=== Dungeon Game (MVC) ===\n")
        print(f"HP: {state.player.hp}   Inventory: {', '.join(state.player.inventory) or '(empty)'}")
        print()

        px, py = state.player.pos
        for y, row in enumerate(state.world.rows):
            line = "".join("P" if (x == px and y == py) else ch for x, ch in enumerate(row))
            print(line)
        print()

        if state.message:
            print(state.message)

        print("\nType: n/s/e/w, look, inv, help, quit")

    def show_help(self) -> str:
        return (
            "Commands:\n"
            "  n,s,e,w  - move\n"
            "  look     - reprint map\n"
            "  inv      - inventory\n"
            "  help     - help\n"
            "  quit     - exit"
        )
