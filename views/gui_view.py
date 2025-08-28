# views/gui_view.py
from __future__ import annotations
import tkinter as tk
from models.game_state import GameState

TILE = 48

COLORS = {
    "wall":        "#4d4d4d",
    "floor":       "#bada9d",
    "player":      "#1f77b4",
    "gold":        "#ffd700",
    "monster":     "#8e44ad",
    "exit_locked": "#e74c3c",
    "exit_open":   "#2ecc71",
    "text":        "#222222",
    "bg":          "#2b2b2b",
    "grid":        "#000000",
    "panel":       "#3b3b3b",
    "button_fg":   "#111111",
}

class GuiView:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Dungeon Game")
        self.canvas = tk.Canvas(self.root, width=1, height=1,
                                bg=COLORS["bg"], highlightthickness=0)
        self.canvas.pack()
        self._on_close = None
        self._start_overlay = None

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
        self.root.mainloop()

    def show_start_screen(self, on_start) -> None:
        """Simple overlay with a Start Game button."""
        if self._start_overlay:
            try: self._start_overlay.destroy()
            except Exception: pass
        overlay = tk.Frame(self.root, bg=COLORS["panel"])
        overlay.place(relx=0.5, rely=0.5, anchor="center")
        title = tk.Label(overlay, text="Dungeon Game", fg="white", bg=COLORS["panel"], font=("TkDefaultFont", 16, "bold"))
        title.pack(padx=20, pady=(16, 8))
        subtitle = tk.Label(
            overlay,
            text="Collect all coins ($) to open the exit gate (E).\nBeware: monsters (▣) roam…",
            fg="white", bg=COLORS["panel"]
        )
        subtitle.pack(padx=20, pady=(0, 12))
        btn = tk.Button(overlay, text="Start Game", command=lambda: (overlay.destroy(), on_start()))
        btn.pack(padx=20, pady=(0, 16))
        self._start_overlay = overlay
        btn.focus_set()

    # -------- rendering --------
    def _resize_canvas(self, state: GameState) -> None:
        w = state.world.width * TILE
        h = state.world.height * TILE + 32
        self.canvas.config(width=w, height=h)

    def render(self, state: GameState) -> None:
        self._resize_canvas(state)
        c = self.canvas
        c.delete("all")

        coins_left = len(state.world.gold)
        gate_color = COLORS["exit_open"] if coins_left == 0 else COLORS["exit_locked"]

        # tiles
        for y, row in enumerate(state.world.rows):
            for x, _ in enumerate(row):
                x0, y0 = x * TILE, y * TILE
                x1, y1 = x0 + TILE, y0 + TILE

                # base tile
                if state.world.is_wall(x, y):
                    c.create_rectangle(x0, y0, x1, y1,
                                       fill=COLORS["wall"], outline=COLORS["grid"])
                else:
                    c.create_rectangle(x0, y0, x1, y1,
                                       fill=COLORS["floor"], outline=COLORS["grid"])

                # exit gate (always visible)
                if (x, y) == state.world.exit:
                    c.create_rectangle(x0 + 8, y0 + 8, x1 - 8, y1 - 8,
                                       fill=gate_color, outline="")

                # coins
                if (x, y) in state.world.gold:
                    c.create_oval(x0 + 14, y0 + 14, x1 - 14, y1 - 14,
                                  fill=COLORS["gold"], outline=COLORS["grid"])

                # monsters (square)
                if (x, y) in state.world.monsters:
                    c.create_rectangle(x0 + 14, y0 + 14, x1 - 14, y1 - 14,
                                       fill=COLORS["monster"], outline=COLORS["grid"])

        # player
        px, py = state.player.pos
        c.create_oval(px * TILE + 6, py * TILE + 6,
                      px * TILE + TILE - 6, py * TILE + TILE - 6,
                      fill=COLORS["player"], outline="white", width=2)

        # HUD
        hud_y = state.world.height * TILE + 16
        status = "Gate OPEN" if coins_left == 0 else f"Gate locked — {coins_left} coin(s) left"
        c.create_text(4, hud_y, anchor="w", fill=COLORS["text"],
                      text=f"HP: {state.player.hp}   Coins: {state.player.gold}   {status}   {state.message or ''}")