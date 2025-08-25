from typing import Tuple
from models.game_state import GameState


class GameController:
    DIRS: dict[str, Tuple[int, int]] = {
        "n": (0, -1),
        "s": (0, 1),
        "w": (-1, 0),
        "e": (1, 0),
    }

    def handle(self, raw: str, state: GameState) -> None:
        cmd = raw.strip().lower()

        if cmd in ("quit", "exit", "q"):
            state.is_over = True
            state.message = "You gave up. Game over."
            return

        if cmd in ("help", "?"):
            from views.console_view import ConsoleView
            state.message = ConsoleView().show_help()
            return

        if cmd in ("inv", "inventory"):
            inv = ", ".join(state.player.inventory) or "(empty)"
            state.message = f"Inventory: {inv}"
            return

        if cmd in ("look", "map"):
            # rendering already shows the map; just a friendly note
            state.message = "You look around…"
            return

        if cmd in self.DIRS:
            dx, dy = self.DIRS[cmd]
            self._move(dx, dy, state)
            return

        state.message = f"Unknown command: {cmd!r}. Type 'help' for options."

    # --- helpers -----------------------------------------------------------

    def _move(self, dx: int, dy: int, state: GameState) -> None:
        px, py = state.player.pos
        nx, ny = px + dx, py + dy
        tile = state.world.tile_at(nx, ny)

        if not state.world.is_walkable(tile):
            state.message = "You bump into a wall."
            return

        # Handle special tiles
        if tile == "$":
            state.player.inventory.append("Gold")
            state.world.set_tile(nx, ny, ".")
            state.player.pos = (nx, ny)
            state.message = "You pick up some Gold!"
            return

        if tile == "E":
            # Simple deterministic combat
            state.player.hp -= 1
            if state.player.hp <= 0:
                state.is_over = True
                state.message = "The monster strikes you down. You died!"
                return
            state.world.set_tile(nx, ny, ".")
            state.player.inventory.append("Fang")
            state.player.pos = (nx, ny)
            state.message = "You slay the monster but take 1 damage."
            return

        if tile == "G":
            state.player.pos = (nx, ny)
            state.is_over = True
            state.did_win = True
            state.message = "You reach the goal! Victory!"
            return

        # Normal floor
        state.player.pos = (nx, ny)
        state.message = "You move."
