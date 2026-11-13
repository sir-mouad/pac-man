"""Snapshot-only maze rendering, with a cached wall layer."""

import math

import pygame

from engine.shared import Direction, GameSnapshot
from frontend.theme import BLUE, GHOSTS, INK, TEAL, WHITE, Painter


ANGLES: dict[Direction | None, float] = {
          None: 0, Direction.RIGHT: 0, Direction.DOWN: math.pi / 2,
          Direction.LEFT: math.pi, Direction.UP: -math.pi / 2}


class MazeRenderer:
    """Draws the maze, pellets, ghosts, and Pac-Man from a game snapshot."""
    def __init__(self, painter: Painter) -> None:
        """Create a renderer that draws with the given painter."""
        self.painter = painter
        self.cache_key: tuple | None = None
        self.layer: pygame.Surface | None = None
        self.motion_key: tuple | None = None
        self.motion: dict[str, tuple[tuple, tuple, float]] = {}

    def position(self, name: str, target: tuple, phase: float,
                 duration: float) -> tuple:
        """Return a smoothly moving position for a sprite."""
        if name not in self.motion:
            self.motion[name] = (target, target, phase)
        start, end, began = self.motion[name]
        amount = max(0, min(1, (phase - began) / duration))
        current = tuple(a + (b - a) * amount for a, b in zip(start, end))
        if end != target:
            if abs(end[0] - target[0]) + abs(end[1] - target[1]) != 1:
                current = target  # respawns and level changes don't slide
            self.motion[name] = (current, target, phase)
        return current

    def draw(self, snap: GameSnapshot, area: pygame.Rect,
             phase: float) -> pygame.Rect:
        """Draw the maze and sprites in area; return the maze rectangle."""
        cell = min(area.width / snap.width, area.height / snap.height)
        width, height = round(cell * snap.width), round(cell * snap.height)
        bounds = pygame.Rect(0, 0, width, height)
        bounds.center = area.center
        motion_key = (id(snap.walls), snap.level, snap.lives)
        if motion_key != self.motion_key:
            self.motion_key = motion_key
            self.motion.clear()
        key = (id(snap.walls), snap.width, snap.height, width, height)
        if key != self.cache_key:
            self.cache_key = key
            self.layer = self._walls(snap, cell, width, height)
        if self.layer is not None:
            self.painter.canvas.blit(self.layer, bounds)

        def center(pos: tuple) -> tuple:
            """Convert a grid cell to screen pixels."""
            return (round(bounds.x + (pos[0] + .5) * cell),
                    round(bounds.y + (pos[1] + .5) * cell))

        canvas = self.painter.canvas
        for pos in snap.pacgums:
            pygame.draw.circle(canvas, (231, 213, 167), center(pos),
                               max(1, round(cell * .065)))
        for pos in snap.super_pacgums:
            radius = max(3, round(cell * (.16 + .035 * math.sin(phase * 5))))
            pygame.draw.circle(canvas, (46, 63, 61), center(pos), radius + 4)
            pygame.draw.circle(canvas, WHITE, center(pos), radius)
        for i, ghost in enumerate(snap.ghosts):
            pos = self.position(f"ghost{i}", ghost.position, phase,
                                ghost.seconds_per_cell)
            self.painter.ghost(center(pos), cell * .31,
                               GHOSTS[i % 4], ghost.edible, phase)
        player = self.position("player", snap.player, phase, .12)
        self.painter.pacman(center(player), cell * .34,
                            ANGLES.get(snap.player_direction, 0), phase)
        return bounds

    @staticmethod
    def _walls(snap: GameSnapshot, cell: float,
               width: int, height: int) -> pygame.Surface:
        """Pre-render the walls onto one surface so drawing stays fast."""
        layer = pygame.Surface((width + 1, height + 1))
        layer.fill(INK)
        lines: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for y, row in enumerate(snap.walls):
            for x, walls in enumerate(row):
                left, top = round(x * cell), round(y * cell)
                right, bottom = round((x + 1) * cell), round((y + 1) * cell)
                if all(walls):
                    pygame.draw.rect(layer, (18, 33, 40),
                                     (left, top, right - left, bottom - top))
                if walls[0]:
                    lines.append(((left, top), (right, top)))
                if walls[3]:
                    lines.append(((left, top), (left, bottom)))
                if x == snap.width - 1 and walls[1]:
                    lines.append(((right, top), (right, bottom)))
                if y == snap.height - 1 and walls[2]:
                    lines.append(((left, bottom), (right, bottom)))
        for start, end in lines:
            pygame.draw.line(layer, (20, 52, 57), start, end, 6)
        for start, end in lines:
            pygame.draw.line(layer, (54, 139, 136), start, end, 3)
            pygame.draw.line(layer, TEAL if cell > 28 else BLUE,
                             start, end, 1)
        return layer
