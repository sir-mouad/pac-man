from enum import Enum


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Phase(Enum):
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    VICTORY = 4
