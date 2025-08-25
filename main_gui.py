# main_gui.py
from __future__ import annotations
from controllers.gui_controller import GUIController
from models.game_state import GameState
from models.player import Player
from models.world import World
from views.gui_view import GuiView

def main() -> None:
    # world & player
    world = World.default()
    player = Player(pos=(1, 1))
    state = GameState(world=world, player=player)

    # view & controller
    view = GuiView()
    controller = GUIController()

    # --- key bindings ---
    def on_key(event) -> None:
        # Normalize to something like "up", "down", "a", "w", etc.
        k = event.keysym.lower()
        controller.handle(k, state)
        view.render(state)
        if state.is_over:
            # Close window shortly after showing final screen
            view.root.after(600, view.root.destroy)

    for keysym in ("Up", "Down", "Left", "Right", "w", "a", "s", "d"):
        view.bind_key(f"<{keysym}>", on_key)

    # Close button: mark game over so the loop can end gracefully
    view.set_on_close(lambda: setattr(state, "is_over", True))

    # Initial draw
    view.render(state)

    # Tk mainloop
    view.mainloop()

if __name__ == "__main__":
    main()
