# controllers/gui_controller.py
from __future__ import annotations
from typing import Tuple
from models.game_state import GameState

class GUIController:
    # Directions in dx, dy
    DIRS: dict[str, Tuple[int, int]] = {
        "n": (0, -1), "up": (0, -1),    "w": (-1, 0), "left": (-1, 0),
        "s": (0, 1),  "down": (0, 1),   "e": (1, 0),  "right": (1, 0),
        "a": (-1, 0), "d": (1, 0),      "w_key": (0, -1), "s_key": (0, 1),
    }

    def handle(self, raw: str, state: GameState) -> None:
        """
        raw is a key label we pass from the GUI (e.g., '<Up>' -> 'up', 'w' -> 'w').
        """
        k = raw.strip().lower()

        # Normalize arrows coming from Tk's event.keysym
        arrow_names = {"up", "down", "left", "right"}
        if k in arrow_names or k in ("w", "a", "s", "d", "n", "e"):
            dx, dy = self._dir(k)
            if dx is None:
                return
            self._move(state, dx, dy)
            return

        if k in ("help", "?"):
            from views.console_view import ConsoleView
            state.message = ConsoleView().show_help()
            return

        if k in ("inv", "inventory"):
            inv = ", ".join(state.player.inventory) or "(empty)"
            state.message = f"Inventory: {inv}"
            return

        # ignore unknown keys quietly
        state.message = ""

    # ---------------- internal helpers ----------------

    def _dir(self, key: str) -> Tuple[int | None, int | None]:
        # Map arrows -> their names, WASD -> arrows-ish
        if key in ("<up>", "up"):
            key = "up"
        elif key in ("<down>", "down"):
            key = "down"
        elif key in ("<left>", "left"):
            key = "left"
        elif key in ("<right>", "right"):
            key = "right"
        elif key == "w":
            key = "up"
        elif key == "s":
            key = "down"
        elif key == "a":
            key = "left"
        elif key == "d":
            key = "right"

        v = self.DIRS.get(key)
        return v if v else (None, None)

    def _move(self, state: GameState, dx: int, dy: int) -> None:
        x, y = state.player.pos
        nx, ny = x + dx, y + dy

        # bounds / wall checks
        if not state.world.in_bounds(nx, ny) or state.world.is_wall(nx, ny):
            state.message = "You bump into a wall."
            return

        # move
        state.player.pos = (nx, ny)
        state.message = ""

        # pickup
        if (nx, ny) in state.world.gold:
            state.world.gold.remove((nx, ny))
            state.player.gold += 1
            state.message = "You picked up gold!"

        # exit (support both attributes)
        exit_xy = getattr(state.world, "exit_pos", getattr(state.world, "exit", None))
        if exit_xy and (nx, ny) == exit_xy:
            state.message = "You found the exit!"
            state.is_over = True
