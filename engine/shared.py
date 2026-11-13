from enum import Enum
from dataclasses import dataclass


class Direction(Enum):
    """Movement directions on the maze grid."""
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class State(Enum):
    """Current status of a game session."""
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4


class Cheat(Enum):
    """Cheat actions used for peer review testing."""
    SKIP = 1
    NOCLIP = 2
    SUPER = 3
    Immortal = 4
    AutoWin = 5
    Reset = 6


@dataclass
class GameSnapshot:
    """Read-only copy of the game state used for drawing."""
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


@dataclass
class GhostView:
    """Position and state of one ghost, used for drawing."""
    position: tuple[int, int]
    edible: bool
    seconds_per_cell: int
