from engine.shared import Direction

REVERSE = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


class GhostBehavior:
    def target(self, level, player, blinky):
        ...

# (Red)
class BlinkyBehavior(GhostBehavior):
    def target(self, level, player, blinky):
        return player.position

# (Pink)
class PinkyBehavior(GhostBehavior):
    def target(self, level, player, blinky):
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
    def target(self, level, player, blinky):
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
    def __init__(self, ghost):
        self.ghost = ghost

    def target(self, level, player, blinky):
        px, py = player.position
        gx, gy = self.ghost.position
        distance = (px - gx) ** 2 + (py - gy) ** 2
        if distance > 64:
            return player.position
        return self.ghost.corner


class GhostAI:
    def __init__(self):
        self.respawn_delay = 3.0
        self.waiting = {}

    def update(self, level, player, ghosts, frame_time):
        for ghost in ghosts:
            if ghost in self.waiting:
                self._update_respawn(ghost, frame_time)
                continue
            direction = self._choose_direction(level, player, ghosts, ghost)
            ghost.set_direction(direction)

    def _choose_direction(self, level, player, ghosts, ghost):
        if ghost.edible:
            return self._flee_direction(level, player, ghost)
        else:
            blinky = None
            for g in ghosts:
                if isinstance(g.behavior, BlinkyBehavior):
                    blinky = g
                    break
            target = ghost.behavior.target(level, player, blinky)
            return self._chase_direction(level, ghost, target)

    def _chase_direction(self, level, ghost, target):
        open_directions = self._open_directions(level, ghost)
        return self._best_direction(level, ghost, target, open_directions)

    def _flee_direction(self, level, player, ghost):
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
        best = None
        best_distance = None
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

    def _open_directions(self, level, ghost):
        walls = level.walls
        x, y = ghost.position
        current_cell = walls[y][x]
        open_directions = []
        if not current_cell[0]:
            open_directions.append(Direction.UP)
        if not current_cell[1]:
            open_directions.append(Direction.RIGHT)
        if not current_cell[2]:
            open_directions.append(Direction.DOWN)
        if not current_cell[3]:
            open_directions.append(Direction.LEFT)

        return open_directions

    def _best_direction(self, level, ghost, target, open_directions):
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
        tx, ty = target
        best = None
        best_distance = None
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
            if best_distance is None or distance < best_distance:
                best = direction
                best_distance = distance
        return best

    def start_respawn(self, ghost):
        self.waiting[ghost] = self.respawn_delay

    def _update_respawn(self, ghost, frame_time):
        self.waiting[ghost] -= frame_time
        if self.waiting[ghost] <= 0:
            del self.waiting[ghost]
            ghost.respawn()
