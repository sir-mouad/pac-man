from enum import Enum
from dataclasses import dataclass, field


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class State(Enum):
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4


@dataclass
class GameSnapshot:
    state: State
    score: int
    lives: int
    level: int
    time_left: float
    player: tuple[int, int]
    player_direction: Direction | None
    ghosts: list["GhostView"]
    walls: list[list[list[bool]]]
    pacgums: set[tuple[int, int]]
    super_pacgums: set[tuple[int, int]]
    width: int
    height: int


@dataclass(frozen=True)
class GhostView:
    position: tuple[int, int]
    edible: bool
