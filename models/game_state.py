# models/game_state.py
from __future__ import annotations

from dataclasses import dataclass, field

from models.player import Player
from models.world import World


@dataclass
class GameState:
    """
    Aggregate state shared between controllers and views.
    """
    world: World
    player: Player
    message: str = ""
    is_over: bool = False
    did_win: bool = False

    # Reserved for future extensibility (e.g., turn counters)
    flags: dict[str, object] = field(default_factory=dict)