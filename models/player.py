# models/player.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


Pos = Tuple[int, int]


@dataclass
class Player:
    """
    Player model used by both console and GUI modes.
    """
    pos: Pos = (1, 1)
    hp: int = 10
    gold: int = 0
    inventory: List[str] = field(default_factory=list)