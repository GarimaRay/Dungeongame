from __future__ import annotations
from typing import Tuple
from models.game_state import GameState
from controllers.game_controller import GameController

class GUIController:
    DIRS: dict[str, Tuple[int, int]] = {
        "n": (0, -1), "up": (0, -1),
        "s": (0,  1), "down": (0,  1),
        "w": (-1, 0), "left": (-1, 0),
        "e": (1,  0), "right": (1,  0),
        "a": (-1, 0), "d": (1, 0),
    }

    def __init__(self) -> None:
        self.core = GameController()  # share rules with console

    def handle(self, raw: str, state: GameState) -> None:
        if state.is_over:
            return  # ignore inputs after game ends

        k = raw.strip().lower()
        arrow = {"up","down","left","right"}
        if k in arrow or k in ("w","a","s","d","n","e"):
            dx, dy = self._dir(k)
            if dx is not None:
                self.core.step(dx, dy, state)
            return

        if k in ("help", "?"):
            from views.console_view import ConsoleView
            state.message = ConsoleView().show_help()
            return

        if k in ("inv", "inventory"):
            inv = ", ".join(state.player.inventory) or "(empty)"
            state.message = f"Inventory: {inv}"
            return

        state.message = ""  # ignore others

    def _dir(self, key: str) -> Tuple[int | None, int | None]:
        if key in ("<up>", "up"): key = "up"
        elif key in ("<down>", "down"): key = "down"
        elif key in ("<left>", "left"): key = "left"
        elif key in ("<right>", "right"): key = "right"
        elif key == "w": key = "up"
        elif key == "s": key = "down"
        elif key == "a": key = "left"
        elif key == "d": key = "right"
        return self.DIRS.get(key, (None, None))