import os
from models.game_state import GameState

class ConsoleView:
    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def render(self, state: GameState) -> None:
        self.clear()
        print("=== Dungeon Game ===\n")
        coins_left = len(state.world.gold)
        gate_status = "OPEN" if coins_left == 0 else f"locked — {coins_left} left"
        print(f"HP: {state.player.hp}   Coins: {state.player.gold}   Gate: {gate_status}")
        print()

        px, py = state.player.pos
        for y, row in enumerate(state.world.rows):
            line_chars = []
            for x, ch in enumerate(row):
                if (x, y) == (px, py):
                    line_chars.append("P")
                elif state.world.is_wall(x, y):
                    line_chars.append("#")
                elif (x, y) in state.world.gold:
                    line_chars.append("$")
                elif (x, y) in state.world.monsters:
                    line_chars.append("M")
                elif (x, y) == state.world.exit:
                    line_chars.append("E")
                else:
                    line_chars.append(".")
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
            "  quit     - exit\n\n"
            "Goal: Collect all coins ($) to open the exit gate (E). Step on E to win.\n"
            "Beware: M = roaming monster. Encounters are random when they’re on/next to you."
        )