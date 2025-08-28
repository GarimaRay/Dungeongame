from __future__ import annotations
from typing import Tuple, Iterable, Optional
from models.game_state import GameState
import random

# Game rules
ENCOUNTER_PROB_ADJ = 0.35   # chance to get hit if a monster ends up adjacent after they move 
ENCOUNTER_PROB_ON  = 0.90   # chance to get hit if a monster ends up on your tile after they move
DAMAGE_ADJ = 1
DAMAGE_ON  = 2
MAX_HP = 1


class GameController:
    DIRS: dict[str, Tuple[int, int]] = {
        "n": (0, -1), "s": (0,  1), "w": (-1, 0), "e": (1, 0)
    }

    # Shared rules (console + GUI call this)
    def step(self, dx: int, dy: int, state: GameState) -> None:
        px, py = state.player.pos
        nx, ny = px + dx, py + dy

        if not state.world.in_bounds(nx, ny) or state.world.is_wall(nx, ny):
            state.message = "You bump into a wall."
            return

        # Move player
        state.player.pos = (nx, ny)
        msgs: list[str] = []

        # --- 1) Immediate collision BEFORE monsters move -------------------
        collided_this_turn = False
        if (nx, ny) in state.world.monsters:
            collided_this_turn = True
            if self._damage(state, DAMAGE_ON):
                state.is_over = True
                state.did_win = False
                state.message = "A monster mauls you! You died!"
                return
            msgs.append(f"You collide with a monster! (-{DAMAGE_ON} HP)")

        # --- 2) Coin pickup -----------------------------------------------
        if (nx, ny) in state.world.gold:
            state.world.gold.remove((nx, ny))
            state.player.gold += 1
            msgs.append("You pick up a coin!")

        # --- 3) Exit gate --------------------------------------------------
        coins_left = len(state.world.gold)
        if (nx, ny) == state.world.exit:
            if coins_left == 0:
                state.is_over = True
                state.did_win = True
                msgs.append("The gate shimmers open… You escape! Victory!")
                state.message = " ".join(msgs)
                return
            else:
                plural = "coins" if coins_left != 1 else "coin"
                # Important: do NOT tick monsters on this step to avoid
                # “I lost while trying the locked gate” confusion.
                hint = self._sense_toward_coin(state)
                state.message = f"The exit gate is sealed. Collect {coins_left} more {plural}." + (f" {hint}" if hint else "")
                return

        # --- 4) Monsters move (random walk) --------------------------------
        self._tick_monsters(state)

        # --- 5) Post-tick random encounter (on/adjacent) -------------------
        # If we already resolved a same-tile collision above, avoid double “on‑tile” hits this turn.
        enc_msg = self._maybe_encounter(state, allow_on_tile=not collided_this_turn)
        if enc_msg:
            # _maybe_encounter sets is_over/message on death; otherwise returns a short string
            if not state.is_over:
                msgs.append(enc_msg)
            else:
                return

        # --- 6) Ambient hints & message -----------------------------------
        hint = self._sense(state)
        state.message = (" ".join(msgs) if msgs else "You move.")
        if hint:
            state.message += f" | {hint}"

    # Text console handler
    def handle(self, raw: str, state: GameState) -> None:
        cmd = raw.strip().lower()

        if state.is_over:
            return  # ignore inputs after end

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
            state.message = "You look around…"
            return

        if cmd in self.DIRS:
            dx, dy = self.DIRS[cmd]
            self.step(dx, dy, state)
            return

        state.message = f"Unknown command: {cmd!r}. Type 'help' for options."

    # -------- helpers --------
    def _damage(self, state: GameState, dmg: int) -> bool:
        state.player.hp = max(0, state.player.hp - dmg)
        return state.player.hp <= 0

    def _tick_monsters(self, state: GameState) -> None:
        """Each monster does a random walk (N/S/E/W if walkable)."""
        new_positions: set[Tuple[int, int]] = set()
        taken = set()  # avoid collapsing multiple monsters into one tile this tick

        def neighbors(x: int, y: int) -> list[Tuple[int, int]]:
            cand = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
            return [(cx, cy) for (cx, cy) in cand
                    if state.world.in_bounds(cx, cy) and not state.world.is_wall(cx, cy)]

        for (mx, my) in list(state.world.monsters):
            opts = neighbors(mx, my)
            if opts:
                random.shuffle(opts)
                dest = None
                for d in opts:
                    if d not in taken:
                        dest = d
                        break
                if dest is None:
                    dest = (mx, my)
            else:
                dest = (mx, my)

            new_positions.add(dest)
            taken.add(dest)

        state.world.monsters = new_positions

    def _maybe_encounter(self, state: GameState, *, allow_on_tile: bool = True) -> str | "":
        """Chance to take damage when monsters are on/adjacent after their move."""
        px, py = state.player.pos
        choices: list[tuple[tuple[int, int], int]] = []

        for (mx, my) in state.world.monsters:
            dist = abs(mx - px) + abs(my - py)
            if dist == 0 and allow_on_tile:
                choices.append(((mx, my), 0))
            elif dist == 1:
                choices.append(((mx, my), 1))

        if not choices:
            return ""

        target, dist = random.choice(choices)
        prob = ENCOUNTER_PROB_ON if dist == 0 else ENCOUNTER_PROB_ADJ
        dmg  = DAMAGE_ON        if dist == 0 else DAMAGE_ADJ

        if random.random() < prob:
            if self._damage(state, dmg):
                state.is_over = True
                state.did_win = False
                state.message = "A monster mauls you! You died!"
                return ""
            return f"A monster claws you! (-{dmg} HP)"
        else:
            return "You hear skittering nearby…"

    # -------- hints (tiny ambient feedback) --------
    @staticmethod
    def _dir_hint(a: Tuple[int, int], b: Tuple[int, int]) -> str:
        ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        if abs(dx) >= abs(dy):
            return "east" if dx > 0 else ("west" if dx < 0 else ("south" if dy > 0 else "north"))
        else:
            return "south" if dy > 0 else "north"

    @staticmethod
    def _nearest(src: Tuple[int, int], targets: Iterable[Tuple[int, int]]) -> Optional[Tuple[Tuple[int, int], int]]:
        best = None
        for t in targets:
            d = abs(t[0]-src[0]) + abs(t[1]-src[1])
            if best is None or d < best[1]:
                best = (t, d)
        return best

    def _sense(self, state: GameState) -> str:
        px, py = state.player.pos
        hints: list[str] = []

        if state.world.gold:
            g = self._nearest((px, py), state.world.gold)
            if g and g[1] <= 4:
                hints.append(f"You hear faint clinks to the {self._dir_hint((px, py), g[0])}.")
        e = state.world.exit
        d_exit = abs(e[0]-px) + abs(e[1]-py)
        if d_exit <= 6:
            hints.append(f"A cool draft from the {self._dir_hint((px, py), e)}.")
        return " ".join(hints[:2])

    def _sense_toward_coin(self, state: GameState) -> str:
        if not state.world.gold:
            return ""
        px, py = state.player.pos
        g = self._nearest((px, py), state.world.gold)
        return f"Coins jingle to the {self._dir_hint((px, py), g[0])}." if g else ""