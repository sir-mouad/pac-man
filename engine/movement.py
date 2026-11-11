
from engine.shared import Direction


class Mover:
    def __init__(self, position, direction=None, seconds_per_cell=0.15):
        self.position = position
        self.direction = direction
        self.requested_direction = None
        self.seconds_per_cell = seconds_per_cell
        self.move_timer = 0.0
        self.protected_time = 0.0

    def can_move(self, level, direction):
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

    def step(self, level, frame_time):
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

    def _next_cell(self, x, y, direction):
        if direction is Direction.UP:
            return (x, y - 1)
        elif direction is Direction.RIGHT:
            return (x + 1, y)
        elif direction is Direction.DOWN:
            return (x, y + 1)
        elif direction is Direction.LEFT:
            return (x - 1, y)

    def set_direction(self, direction):
        self.requested_direction = direction


class Player(Mover):
    def __init__(self, start):
        super().__init__(start, direction=None, seconds_per_cell=0.15)
        self.start = start
        self.walk_through_walls = False

    def reset(self, start):
        self.position = start
        self.direction = None
        self.requested_direction = None
        self.move_timer = 0.0


class Ghost(Mover):
    def __init__(self, corner, level_number):
        super().__init__(corner, direction=None, seconds_per_cell=0.25)
        self.corner = corner
        self.level_number = level_number
        self.edible = False

    def respawn(self):
        self.position = self.corner
        self.direction = None
        self.requested_direction = None
        self.move_timer = 0.0
        self.edible = False
        self.seconds_per_cell =  0.30 - (self.level_number - 1) * 0.01
