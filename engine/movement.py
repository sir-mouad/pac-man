
from typing import Any

from engine.shared import Direction


class Mover:
    """Base class for a sprite that moves one cell at a time."""
    def __init__(self, position: tuple[int, int],
                 direction: Direction | None = None,
                 seconds_per_cell: Any = None) -> None:
        """Set the starting cell, direction, and speed."""
        self.position = position
        self.direction = direction
        self.requested_direction: Direction | None = None
        self.seconds_per_cell = seconds_per_cell
        self.move_timer = 0.0
        self.protected_time = 0.0

    def can_move(self, level: Any,
                 direction: Direction | None) -> bool:
        """Return True if the sprite can step in this direction."""
        if getattr(self, "walk_through_walls", False):
            x, y = self.position
            x, y = self._next_cell(x, y, direction)
            if x < 0 or x >= level.width or y < 0 or y >= level.height:
                return False
            return True

        walls = level.walls
        x, y = self.position
        current_cell = walls[y][x]

        if direction is Direction.UP:
            return not current_cell[0]
        if direction is Direction.RIGHT:
            return not current_cell[1]
        if direction is Direction.DOWN:
            return not current_cell[2]
        if direction is Direction.LEFT:
            return not current_cell[3]

        return False

    def step(self, level: Any, frame_time: float) -> None:
        """Advance the timer and move one cell when it is time."""
        self.move_timer += frame_time

        if self.move_timer < self.seconds_per_cell:
            return

        self.move_timer -= self.seconds_per_cell

        if self.requested_direction is not None:
            if self.can_move(level, self.requested_direction):
                self.direction = self.requested_direction
                self.requested_direction = None

        if self.direction is None:
            return

        if not self.can_move(level, self.direction):
            return

        x, y = self.position
        self.position = self._next_cell(x, y, self.direction)

    def _next_cell(self, x: int, y: int, direction: Any) -> Any:
        """Return the cell next to (x, y) in the given direction."""
        if direction is Direction.UP:
            return (x, y - 1)
        elif direction is Direction.RIGHT:
            return (x + 1, y)
        elif direction is Direction.DOWN:
            return (x, y + 1)
        elif direction is Direction.LEFT:
            return (x - 1, y)

    def set_direction(self, direction: Direction | None) -> None:
        """Store the direction to turn to at the next cell."""
        self.requested_direction = direction


class Player(Mover):
    """The Pac-Man sprite controlled by the player."""
    def __init__(self, start: tuple[int, int]) -> None:
        """Create the player at its start cell."""
        super().__init__(start, direction=None, seconds_per_cell=0.15)
        self.start = start
        self.walk_through_walls = False

    def reset(self, start: tuple[int, int]) -> None:
        """Move the player back to start and stop it."""
        self.position = start
        self.direction = None
        self.requested_direction = None
        self.move_timer = 0.0


class Ghost(Mover):
    """A ghost that chases the player, flees when edible, and respawns."""
    behavior: Any  # chase strategy, set by GameEngine

    def __init__(self, corner: tuple[int, int], level_number: int) -> None:
        """Create a ghost that starts from its corner."""
        super().__init__(corner, direction=None, seconds_per_cell=0.45)
        self.corner = corner
        self.level_number = level_number
        self.first_seconds = self.seconds_per_cell
        self.edible = False

    def respawn(self) -> None:
        """Send the ghost back to its corner and reset its speed."""
        self.position = self.corner
        self.direction = None
        self.requested_direction = None
        self.move_timer = 0.0
        self.edible = False
        if self.level_number <= 7:
            self.seconds_per_cell = self.first_seconds - \
                (self.level_number - 1) * 0.01
        elif self.level_number <= 11:
            self.seconds_per_cell = self.first_seconds - \
                (self.level_number - 1) * 0.02
        else:
            self.seconds_per_cell = self.first_seconds - \
                10 * 0.02
