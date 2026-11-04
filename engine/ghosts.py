from contracts import Direction

OPPOSITE = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


class GhostBehavior:
    def target(self, level, player, blinky):
        ...


class BlinkyBehavior(GhostBehavior):
    def target(self, level, player, blinky):
        return player.position


class PinkyBehavior(GhostBehavior):
    def target(self, level, player, blinky):
        x, y = player.position
        if player.direction is Direction.UP:
            x, y = x, y - 4
        if player.direction is Direction.RIGHT:
            x, y = x + 4, y
        if player.direction is Direction.DOWN:
            x, y = x, y + 4
        if player.direction is Direction.LEFT:
            x, y = x - 4, y
        x = max(0, min(x, level.width - 1))
        y = max(0, min(y, level.height - 1))
        return x, y


# the only one use blinky positions
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
        vector_x = 2 * (px - x1)
        vector_y = 2 * (py - y1)
        x = max(0, min(x + vector_x, level.width - 1))
        y = max(0, min(y + vector_y, level.height - 1))
        return x, y

# Calculate the Euclidean distance
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
    def __init__(self, rng, respawn_delay):
        self.rng = rng
        self.respawn_delay = respawn_delay

    def update(self, level, player, ghosts):
        ...

    def _choose_direction(self, level, player, ghosts, ghost):
        ...

    def _chase_direction(self, level, ghost, target):
        ...

    def _flee_direction(self, level, player, ghost):
        ...

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
            back = OPPOSITE[ghost.direction]
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

    def _pick_fallback(self, level, ghost):
        ...

    def _update_respawn(self, level, ghost):
        ...
