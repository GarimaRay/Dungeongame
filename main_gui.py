# main_gui.py
from __future__ import annotations
from controllers.gui_controller import GUIController
from models.game_state import GameState
from models.player import Player
from models.world import World
from views.gui_view import GuiView

def main() -> None:
    world = World.default()
    player = Player(pos=(1, 1))
    state = GameState(world=world, player=player)

    view = GuiView()
    controller = GUIController()

    def on_key(event) -> None:
        if state.is_over:
            return
        k = event.keysym.lower()
        controller.handle(k, state)
        view.render(state)
        if state.is_over:
            view.show_end_screen(state.did_win, state.message, on_quit=lambda: view.root.destroy())

    def start_game() -> None:
        for keysym in ("Up", "Down", "Left", "Right", "w", "a", "s", "d"):
            view.bind_key(f"<{keysym}>", on_key)
        view.render(state)
        view.root.focus_set()

    view.set_on_close(lambda: setattr(state, "is_over", True))
    view.render(state)
    view.show_start_screen(start_game)
    view.mainloop()

if __name__ == "__main__":
    main()