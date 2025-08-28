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

    # --- key bindings set up AFTER Start is pressed ---
    def on_key(event) -> None:
        k = event.keysym.lower()
        controller.handle(k, state)
        view.render(state)
        if state.is_over:
            view.root.after(1200, view.root.destroy)

    def start_game() -> None:
        # Bind keys now that the player started
        for keysym in ("Up", "Down", "Left", "Right", "w", "a", "s", "d"):
            view.bind_key(f"<{keysym}>", on_key)
        view.render(state)
        view.root.focus_set()

    # Close button: mark game over so the loop can end gracefully
    view.set_on_close(lambda: setattr(state, "is_over", True))

    # Initial draw (map under the overlay), then show Start
    view.render(state)
    view.show_start_screen(start_game)

    # Tk mainloop
    view.mainloop()

if __name__ == "__main__":
    main()