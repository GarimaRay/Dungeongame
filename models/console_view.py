# views/console_view.py
from __future__ import annotations

import os

from models.game_state import GameState


class ConsoleView:
    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def render(self, state: GameState) -> None:
        self.clear()
        print("=== Dungeon Game (MVC) ===\n")
        print(
            f"HP: {state.player.hp}   "
            f"Gold: {state.player.gold}   "
            f"Inventory: {', '.join(state.player.inventory) or '(empty)'}"
        )
        print()

        px, py = state.player.pos
        for y in range(state.world.height):
            line_chars = []
            for x in range(state.world.width):
                if (x, y) == (px, py):
                    line_chars.append("P")
                else:
                    line_chars.append(state.world.tile_at(x, y))
            print("".join(line_chars))
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