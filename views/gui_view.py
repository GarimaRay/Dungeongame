# views/gui_view.py
from __future__ import annotations
import tkinter as tk
from models.game_state import GameState

TILE = 48

COLORS = {
    "wall":  "#4d4d4d",
    "floor": "#bada9d",
    "player": "#1f77b4",
    "gold":  "#ffd700",
    "exit":  "#e74c3c",
    "text":  "#222222",
    "bg":    "#2b2b2b",
    "grid":  "#000000",
}

class GuiView:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Dungeon Game")
        self.canvas = tk.Canvas(self.root, width=1, height=1,
                                bg=COLORS["bg"], highlightthickness=0)
        self.canvas.pack()
        self._on_close = None  # set by set_on_close()

    # -------- integration helpers --------
    def bind_key(self, key: str, func) -> None:
        self.root.bind(key, func)

    def set_on_close(self, handler) -> None:
        self._on_close = handler

        def _wrapped():
            try:
                if self._on_close:
                    self._on_close()
            finally:
                self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", _wrapped)

    def mainloop(self) -> None:
        """Allow main_gui.py to call view.mainloop()."""
        self.root.mainloop()

    # -------- rendering --------
    def _resize_canvas(self, state: GameState) -> None:
        w = state.world.width * TILE
        h = state.world.height * TILE + 32
        self.canvas.config(width=w, height=h)

    def render(self, state: GameState) -> None:
        self._resize_canvas(state)
        c = self.canvas
        c.delete("all")

        # tiles
        for y, row in enumerate(state.world.rows):
            for x, _ in enumerate(row):
                x0, y0 = x * TILE, y * TILE
                x1, y1 = x0 + TILE, y0 + TILE
                if state.world.is_wall(x, y):
                    c.create_rectangle(x0, y0, x1, y1,
                                       fill=COLORS["wall"], outline=COLORS["grid"])
                else:
                    c.create_rectangle(x0, y0, x1, y1,
                                       fill=COLORS["floor"], outline=COLORS["grid"])
                if (x, y) == state.world.exit:
                    c.create_rectangle(x0 + 8, y0 + 8, x1 - 8, y1 - 8,
                                       fill=COLORS["exit"], outline="")
                if (x, y) in state.world.gold:
                    c.create_oval(x0 + 14, y0 + 14, x1 - 14, y1 - 14,
                                  fill=COLORS["gold"], outline=COLORS["grid"])

        # player
        px, py = state.player.pos
        c.create_oval(px * TILE + 6, py * TILE + 6,
                      px * TILE + TILE - 6, py * TILE + TILE - 6,
                      fill=COLORS["player"], outline="white", width=2)

        # HUD
        hud_y = state.world.height * TILE + 16
        c.create_text(4, hud_y, anchor="w", fill=COLORS["text"],
                      text=f"HP: {state.player.hp}   Gold: {state.player.gold}   {state.message or ''}")
