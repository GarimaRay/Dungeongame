from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Player:
    pos: Tuple[int, int] = (1, 1)
    hp: int = 10
    gold: int = 0
    inventory: List[str] = field(default_factory=list)
