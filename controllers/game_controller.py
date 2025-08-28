from __future__ import annotations
from typing import Tuple, Iterable, Optional
from models.game_state import GameState
import random

# Tune difficulty here:
ENCOUNTER_PROB_NEAR = 0.35   # chance to meet a monster when it's on/adjacent to you
MAX_HP = 10


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

        # Coin pickup
        if (nx, ny) in state.world.gold:
            state.world.gold.remove((nx, ny))
            state.player.gold += 1
            msgs.append("You pick up a coin!")

        # Exit gate: locked until all coins collected
        coins_left = len(state.world.gold)
        if (nx, ny) == state.world.exit:
            if coins_left == 0:
                state.is_over = True
                state.did_win = True
                msgs.append("The gate shimmers open… You escape! Victory!")
            else:
                plural = "coins" if coins_left != 1 else "coin"
                msgs.append(f"The exit gate is sealed. Collect {coins_left} more {plural}.")
                # keep playing

        # If the player just won, stop here (no more monster ticks)
        if state.is_over:
            state.message = " ".join(msgs)
            return

        # Monsters take a random step each turn
        self._tick_monsters(state)

        # Random encounter if any monster is on or adjacent to player
        enc_msg = self._maybe_encounter(state)
        if enc_msg:
            msgs.append(enc_msg)

        # Light “smart” hints (nearby coin + exit direction)
        hint = self._sense(state)
        state.message = (" ".join(msgs) if msgs else "You move.")
        if hint:
            state.message += f" | {hint}"

    # Text console handler
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
            state.message = "You look around…"
            return

        if cmd in self.DIRS:
            dx, dy = self.DIRS[cmd]
            self.step(dx, dy, state)
            return

        state.message = f"Unknown command: {cmd!r}. Type 'help' for options."

    # -------- monster system (tiny & fast) --------
    def _tick_monsters(self, state: GameState) -> None:
        """Each monster does a random walk (N/S/E/W if walkable)."""
        new_positions: set[Tuple[int, int]] = set()
        taken = set()  # avoid collapsing multiple monsters into one tile in a single tick

        def neighbors(x: int, y: int) -> list[Tuple[int, int]]:
            cand = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
            return [(cx, cy) for (cx, cy) in cand
                    if state.world.in_bounds(cx, cy) and not state.world.is_wall(cx, cy)]

        for (mx, my) in list(state.world.monsters):
            opts = neighbors(mx, my)
            if opts:
                random.shuffle(opts)
                # Prefer a free destination this tick; otherwise, stay put
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

    def _maybe_encounter(self, state: GameState) -> str | "":
        """If a monster is on/adjacent to the player, chance to lose 1 HP and remove that monster."""
        px, py = state.player.pos

        # Find any monster with distance <= 1 (includes same tile)
        nearby = [(mx, my) for (mx, my) in state.world.monsters
                  if abs(mx - px) + abs(my - py) <= 1]

        if not nearby:
            return ""

        target = random.choice(nearby)
        if random.random() < ENCOUNTER_PROB_NEAR:
            # Take 1 damage and remove the encountered monster (it "flees" after striking)
            state.world.monsters.remove(target)
            state.player.hp -= 1
            if state.player.hp <= 0:
                state.is_over = True
                state.message = "A roaming monster ambushes you! You collapse…"
                return ""
            return "A roaming monster ambushes you! (-1 HP)"
        else:
            # Near miss
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

        # Nearby coin (within 4 steps)
        if state.world.gold:
            g = self._nearest((px, py), state.world.gold)
            if g and g[1] <= 4:
                hints.append(f"You hear faint clinks to the {self._dir_hint((px, py), g[0])}.")

        # Breeze from exit (within 6 steps)
        e = state.world.exit
        d_exit = abs(e[0]-px) + abs(e[1]-py)
        if d_exit <= 6:
            hints.append(f"A cool draft from the {self._dir_hint((px, py), e)}.")

        return " ".join(hints[:2])