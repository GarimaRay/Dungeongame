# models/world.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Set, Optional
import random

Pos = Tuple[int, int]


@dataclass
class World:
    # Base map: '#' wall, '.' floor (no tokens baked in)
    rows: List[str]

    # Derived sizes
    width: int = field(init=False)
    height: int = field(init=False)

    # Gameplay objects
    gold: Set[Pos] = field(default_factory=set)      # coin locations
    monsters: Set[Pos] = field(default_factory=set)  # monster locations
    exit: Pos = (1, 1)                               # exit gate location

    @property
    def exit_pos(self) -> Pos:
        return self.exit  # back-compat alias

    def __post_init__(self) -> None:
        self.height = len(self.rows)
        self.width = max((len(r) for r in self.rows), default=0)
        self.rows = [r.ljust(self.width, ".") for r in self.rows]

    # ---------- helpers ----------
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_wall(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.rows[y][x] == "#"

    def floor_positions(self) -> List[Pos]:
        return [
            (x, y)
            for y, row in enumerate(self.rows)
            for x, ch in enumerate(row)
            if ch != "#"
        ]

    def populate(
        self,
        start: Pos = (1, 1),
        n_coins: int = 5,
        n_monsters: int = 3,
        seed: Optional[int] = None,
    ) -> None:
        """Place coins and monsters on floor tiles (not on start/exit)."""
        rng = random.Random(seed)
        floors = [p for p in self.floor_positions() if p not in (start, self.exit)]
        rng.shuffle(floors)

        n_coins = max(1, min(n_coins, len(floors)))
        self.gold = set(floors[:n_coins])

        rest = floors[n_coins:]
        rng.shuffle(rest)
        n_monsters = max(0, min(n_monsters, len(rest)))
        self.monsters = set(rest[:n_monsters])

    # ---------- factory ----------
    @classmethod
    def default(cls) -> "World":
        # Slightly larger, still friendly map (15x9).
        rows = [
            "###############",
            "#.............#",
            "#.###.###.###.#",
            "#...#.....#...#",
            "#...###.#.##..#",
            "#.....#.#.....#",
            "#.##..#...###.#",
            "#.............#",
            "###############",
        ]
        w = cls(rows)
        w.exit = (w.width - 2, w.height - 2)  # bottom-right inside the wall frame
        w.populate(start=(1, 1), n_coins=5, n_monsters=3)
        return w