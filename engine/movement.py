from contracts import Direction


class Mover():
    def __init__(self, position, direction=None):
        self.position = position
        self.direction = direction
        self.requested_direction = None

    def can_move(self, level, direction):
        walls = level.walls
        x, y = self.position
        current_cell = walls[y][x]
        if direction is Direction.UP:
            if not current_cell[0]:
                return True
        if direction is Direction.RIGHT:
            if not current_cell[1]:
                return True
        if direction is Direction.DOWN:
            if not current_cell[2]:
                return True
        if direction is Direction.LEFT:
            if not current_cell[3]:
                return True
        return False

    def step(self, level):
        if self.requested_direction is not None:
            if self.can_move(level, self.requested_direction):
                self.direction = self.requested_direction
                self.requested_direction = None
        if self.direction is None:
            return
        x, y = self.position
        if self.can_move(level, self.direction):
            if self.direction is Direction.UP:
                self.position = (x, y-1)
            if self.direction is Direction.RIGHT:
                self.position = (x+1, y)
            if self.direction is Direction.DOWN:
                self.position = (x, y+1)
            if self.direction is Direction.LEFT:
                self.position = (x-1, y)

    def set_direction(self, direction):
        self.requested_direction = direction


class Player(Mover):
    def __init__(self, start):
        super().__init__(start, direction=None)

    def reset(self, start):
        self.position = start
        self.direction = None
        self.requested_direction = None


class Ghost(Mover):
    def __init__(self, corner):
        super().__init__(corner, direction=None)
        self.corner = corner
        self.edible = False

    def respawn(self):
        self.position = self.corner
        self.direction = None
        self.requested_direction = None
        self.edible = False
