# models/world.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Set

     # --- Back-compat alias so older code using `exit_pos` still works ---
@property
def exit_pos(self) -> tuple[int, int]:
        return self.exit


@dataclass
class World:
    # The map as rows of characters: '#' wall, '.' floor
    rows: List[str]

    # Derived sizes
    width: int = field(init=False)
    height: int = field(init=False)

    # Gameplay objects
    gold: Set[Pos] = field(default_factory=set)
    exit: Pos = (1, 1)

    def __post_init__(self) -> None:
        self.height = len(self.rows)
        self.width = max((len(r) for r in self.rows), default=0)
        # normalize to same width (pad floors) so indexing is safe
        self.rows = [r.ljust(self.width, ".") for r in self.rows]

    # ---------- helpers used by views/controllers ----------
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_wall(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.rows[y][x] == "#"

    # ---------- factory with sample map ----------
    @classmethod
    def default(cls) -> "World":
        rows = [
            "#############",
            "#..$...E..G#",
            "#.###.###..#",
            "#..#.......#",
            "##..#.###...",
            "#......#...#",
            "#############",
        ]
        w = cls(rows)

        # Parse special tiles ($ gold, E exit) into structured fields,
        # and convert them to floor (.) in the rows for rendering logic.
        gold: Set[Pos] = set()
        exit_pos: Pos | None = None

        new_rows: List[str] = []
        for y, r in enumerate(w.rows):
            row_chars = list(r)
            for x, ch in enumerate(row_chars):
                if ch == "$":
                    gold.add((x, y))
                    row_chars[x] = "."
                elif ch == "E":
                    exit_pos = (x, y)
                    row_chars[x] = "."
            new_rows.append("".join(row_chars))

        w.rows = new_rows
        w.gold = gold
        if exit_pos is not None:
            w.exit = exit_pos
        return w
