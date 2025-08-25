from __future__ import annotations
from dataclasses import dataclass
from models.world import World
from models.player import Player

@dataclass
class GameState:
    world: World
    player: Player
    message: str = ""
    is_over: bool = False
