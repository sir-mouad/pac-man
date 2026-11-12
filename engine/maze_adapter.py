from collections import deque

from mazegenerator import MazeGenerator
from dataclasses import dataclass, field
from engine.parser import Parser


@dataclass
class Level:
    width: int
    height: int
    walls: list[list[int]]
    pacgums: set[tuple[int, int]] = field(default_factory=set)
    super_pacgums: set[tuple[int, int]] = field(default_factory=set)
    player_start: tuple[int, int] = (0, 0)
    ghost_starts: list[tuple[int, int]] = field(default_factory=list)


class MazeAdapter():
    def __init__(self, config):
        self.config = config

    def generate_level(self, index):
        size = self._level_size(index)
        seed = self._level_seed(index)
        try:
            maze = MazeGenerator(size, perfect=False, seed=seed)
        except Exception as e:
            print(f"Error: level {index} is too large for the ")
            (f"maze package ({e})")
            exit(1)
        walls = self._decode_walls(maze.maze)
        level = Level(width=size[0], height=size[1], walls=walls)
        self._place_ghosts_and_player(level)
        self._place_super_pacgums(level)
        self._place_pacgums(level)
        return level

    def _level_size(self, index):
        level = self.config["levels"][index - 1]
        return (level["width"], level["height"])

    def _level_seed(self, index):
        if index == 1:
            return self.config["seed"]
        return 0

    def _decode_walls(self, grid):
        decoded = []
        for row in grid:
            decoded_row = []
            for value in row:
                decoded_row.append([
                    (value // 1) % 2 == 1,
                    (value // 2) % 2 == 1,
                    (value // 4) % 2 == 1,
                    (value // 8) % 2 == 1,
                ])
            decoded.append(decoded_row)
        return decoded

    def _place_pacgums(self, level):
        for y in range(level.height):
            for x in range(level.width):
                if all(level.walls[y][x]):
                    continue
                if (x, y) in level.super_pacgums:
                    continue
                if (x, y) == level.player_start:
                    continue
                level.pacgums.add((x, y))

    def _place_super_pacgums(self, level):
        corners = [
            (0, 0),
            (level.width - 1, 0),
            (0, level.height - 1),
            (level.width - 1, level.height - 1),
        ]
        level.super_pacgums = {
            self._search_open_cell(level, x, y) for x, y in corners
        }

    def _place_ghosts_and_player(self, level):
        middle = (level.width // 2, level.height // 2)
        level.player_start = self._search_open_cell(level, *middle)

        corners = [
            (0, 0),
            (level.width - 1, 0),
            (0, level.height - 1),
            (level.width - 1, level.height - 1),
        ]
        level.ghost_starts = [
            self._search_open_cell(level, x, y) for x, y in corners
        ]

    def _search_open_cell(self, level, x, y):
        if not all(level.walls[y][x]):
            return x, y
        queue = deque([(x, y)])
        visited = {(x, y)}
        while queue:
            cx, cy = queue.popleft()
            for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < level.width and 0 <= ny < level.height):
                    continue
                if (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                if not all(level.walls[ny][nx]):
                    return nx, ny
                queue.append((nx, ny))
        return x, y
