import os
from typing import Iterable
from models.game_state import GameState


class ConsoleView:
    def clear(self) -> None:
        # Clear screen on Windows/Unix
        os.system("cls" if os.name == "nt" else "clear")

    def render(self, state: GameState) -> None:
        self.clear()
        print("=== Dungeon Game (MVC) ===\n")
        print(f"HP: {state.player.hp}   Inventory: {self._fmt_list(state.player.inventory)}")
        print()

        # draw map with player overlay
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
            "  look     - reprint the map and status\n"
            "  inv      - show inventory\n"
            "  help     - show this help\n"
            "  quit     - exit the game"
        )

    @staticmethod
    def _fmt_list(items: Iterable[str]) -> str:
        return ", ".join(items) if items else "(empty)"
