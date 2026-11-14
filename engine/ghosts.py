from typing import Any
from abc import ABC, abstractmethod
from engine.shared import Direction
from collections import deque
REVERSE = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


class GhostBehavior(ABC):
    """Base class for the strategy each ghost uses to pick its target."""
    @abstractmethod
    def target(
            self, level: Any, player: Any, blinky: Any) -> tuple[int, int]:
        """Return the cell this ghost wants to reach."""
        ...

# (Red)


class BlinkyBehavior(GhostBehavior):
    """Red ghost: chases the player's exact cell."""
    def target(self, level: Any, player: Any, blinky: Any) -> Any:
        """Return the player's current cell."""
        return player.position

# (Pink)


class PinkyBehavior(GhostBehavior):
    """Pink ghost: aims four cells ahead of the player."""
    def target(self, level: Any, player: Any, blinky: Any) -> tuple[int, int]:
        """Return the cell four steps ahead of the player, inside the maze."""
        x, y = player.position
        if player.direction is Direction.UP:
            x, y = x - 4, y - 4
        if player.direction is Direction.RIGHT:
            x, y = x + 4, y
        if player.direction is Direction.DOWN:
            x, y = x, y + 4
        if player.direction is Direction.LEFT:
            x, y = x - 4, y
        x = max(0, min(x, level.width - 1))
        y = max(0, min(y, level.height - 1))
        return x, y


# (Cyan / Blue) ---> the only one use blinky positions
class InkyBehavior(GhostBehavior):
    """Cyan ghost: aims using the player's position and Blinky's position."""
    def target(self, level: Any, player: Any, blinky: Any) -> tuple[int, int]:
        """Return a target found from the player's and Blinky's positions."""
        px, py = player.position
        x, y = px, py
        if player.direction is Direction.UP:
            x, y = px, py - 2
        if player.direction is Direction.RIGHT:
            x, y = px + 2, py
        if player.direction is Direction.DOWN:
            x, y = px, py + 2
        if player.direction is Direction.LEFT:
            x, y = px - 2, py
        x1, y1 = blinky.position
        vector_x = 2 * (x - x1)
        vector_y = 2 * (y - y1)
        x = max(0, min(x + vector_x, level.width - 1))
        y = max(0, min(y + vector_y, level.height - 1))
        return x, y

# (Orange) ---> Calculate the Euclidean distance


class ClydeBehavior(GhostBehavior):
    """Orange ghost: chases from far away, retreats when close."""
    def __init__(self, ghost: Any) -> None:
        """Store the ghost so the behavior can read its position and corner."""
        self.ghost = ghost

    def target(self, level: Any, player: Any, blinky: Any) -> Any:
        """Chase from far away, or retreat to the corner when close."""
        px, py = player.position
        gx, gy = self.ghost.position
        distance = (px - gx) ** 2 + (py - gy) ** 2
        if distance > 64:
            return player.position
        return self.ghost.corner


class GhostAI:
    """Chooses each ghost's direction and handles respawn delays."""
    def __init__(self) -> None:
        """Create the AI with a 3-second respawn delay."""
        self.respawn_delay = 3.0
        self.waiting: dict[Any, float] = {}

    def update(self, level: Any, player: Any, ghosts: list[Any],
               frame_time: float) -> None:
        """Choose a direction for each ghost; count down respawn timers."""
        for ghost in ghosts:
            if ghost in self.waiting:
                self._update_respawn(ghost, frame_time)
                continue
            direction = self._choose_direction(level, player, ghosts, ghost)
            ghost.set_direction(direction)

    def _choose_direction(self, level: Any, player: Any, ghosts: list[Any],
                          ghost: Any) -> Direction | None:
        """Flee from the player if edible, otherwise chase the target."""
        if ghost.edible:
            return self._flee_direction(level, player, ghost)
        else:
            blinky: Any = None
            for g in ghosts:
                if isinstance(g.behavior, BlinkyBehavior):
                    blinky = g
                    break
            target = ghost.behavior.target(level, player, blinky)
            return self._chase_direction(level, ghost, target)

    def _chase_direction(self, level: Any, ghost: Any,
                         target: tuple[int, int]) -> Direction | None:
        """Pick the open direction that gets closest to the target."""
        open_directions = self._open_directions(level, ghost)
        return self._best_direction(level, ghost, target, open_directions)

    def _flee_direction(self, level: Any, player: Any,
                        ghost: Any) -> Direction | None:
        """Pick the open direction that gets farthest from the player."""
        open_directions = self._open_directions(level, ghost)
        if not open_directions:
            return None
        if len(open_directions) == 1:
            return open_directions[0]

        choices = list(open_directions)
        if ghost.direction is not None:
            back = REVERSE[ghost.direction]
            if back in choices and len(choices) > 1:
                choices.remove(back)

        x, y = ghost.position
        tx, ty = player.position
        best: Direction | None = None
        best_distance: int | None = None
        for direction in choices:
            if direction is Direction.UP:
                nx, ny = x, y - 1
            if direction is Direction.RIGHT:
                nx, ny = x + 1, y
            if direction is Direction.DOWN:
                nx, ny = x, y + 1
            if direction is Direction.LEFT:
                nx, ny = x - 1, y
            distance = (nx - tx) ** 2 + (ny - ty) ** 2
            if best_distance is None or distance > best_distance:
                best = direction
                best_distance = distance
        return best

    def _open_directions(self, level: Any, ghost: Any) -> list[Direction]:
        """List the directions the ghost can move without hitting a wall."""
        walls = level.walls
        x, y = ghost.position
        current_cell = walls[y][x]
        open_directions: list[Direction] = []
        if not current_cell[0]:
            open_directions.append(Direction.UP)
        if not current_cell[1]:
            open_directions.append(Direction.RIGHT)
        if not current_cell[2]:
            open_directions.append(Direction.DOWN)
        if not current_cell[3]:
            open_directions.append(Direction.LEFT)

        return open_directions

    def _path_steps(self, level: Any, start: tuple[int, int],
                    target: tuple[int, int]) -> int:
        """Count the steps from start to target using breadth-first search."""
        if start == target:
            return 0
        sides = {(0, -1): 0, (1, 0): 1, (0, 1): 2, (-1, 0): 3}
        queue = deque([(start, 0)])
        visited = {start}
        while queue:
            (cx, cy), steps = queue.popleft()
            for (dx, dy), side in sides.items():
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < level.width and 0 <= ny < level.height):
                    continue
                if (nx, ny) in visited:
                    continue
                if level.walls[cy][cx][side]:
                    continue
                if (nx, ny) == target:
                    return steps + 1
                visited.add((nx, ny))
                queue.append(((nx, ny), steps + 1))
        return 10**10

    def _best_direction(
            self, level: Any, ghost: Any, target: tuple[int, int],
            open_directions: list[Direction]) -> Direction | None:
        """Pick the open direction with the shortest path to the target."""
        if not open_directions:
            return None
        if len(open_directions) == 1:
            return open_directions[0]

        choices = list(open_directions)
        if ghost.direction is not None:
            back = REVERSE[ghost.direction]
            if back in choices and len(choices) > 1:
                choices.remove(back)

        x, y = ghost.position
        best: Direction | None = None
        best_steps: int | None = None
        for direction in choices:
            if direction is Direction.UP:
                nx, ny = x, y - 1
            if direction is Direction.RIGHT:
                nx, ny = x + 1, y
            if direction is Direction.DOWN:
                nx, ny = x, y + 1
            if direction is Direction.LEFT:
                nx, ny = x - 1, y
            steps = self._path_steps(level, (nx, ny), target)
            if best_steps is None or steps < best_steps:
                best = direction
                best_steps = steps
        return best

    def start_respawn(self, ghost: Any) -> None:
        """Start the respawn countdown for an eaten ghost."""
        self.waiting[ghost] = self.respawn_delay

    def _update_respawn(self, ghost: Any, frame_time: float) -> None:
        """Count down the respawn timer and respawn the ghost at zero."""
        self.waiting[ghost] -= frame_time
        if self.waiting[ghost] <= 0:
            del self.waiting[ghost]
            ghost.respawn()
