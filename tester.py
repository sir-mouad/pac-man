import sys

import pygame

from parser import Parser
from maze_adapter import MazeAdapter

CELL = 28
WALL = 4
MARGIN = 20
HUD = 40

BLACK = (0, 0, 0)
BLUE = (33, 33, 222)
WHITE = (255, 255, 255)
PINK = (255, 184, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 184, 82)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)


def cell_center(x, y):
    return (MARGIN + x * CELL + CELL // 2,
            MARGIN + y * CELL + CELL // 2 + HUD)


def draw_walls(screen, level):
    for y in range(level.height):
        for x in range(level.width):
            north, east, south, west = level.walls[y][x]
            left = MARGIN + x * CELL
            top = MARGIN + y * CELL + HUD
            right = left + CELL
            bottom = top + CELL
            if north:
                pygame.draw.line(screen, BLUE, (left, top), (right, top), WALL)
            if east:
                pygame.draw.line(screen, BLUE, (right, top), (right, bottom), WALL)
            if south:
                pygame.draw.line(screen, BLUE, (left, bottom), (right, bottom), WALL)
            if west:
                pygame.draw.line(screen, BLUE, (left, top), (left, bottom), WALL)


def draw_level(screen, level, font, label):
    screen.fill(BLACK)
    draw_walls(screen, level)

    for x, y in level.pacgums:
        pygame.draw.circle(screen, PINK, cell_center(x, y), 3)
    for x, y in level.super_pacgums:
        pygame.draw.circle(screen, WHITE, cell_center(x, y), 7)

    px, py = level.player_start
    pygame.draw.circle(screen, YELLOW, cell_center(px, py), CELL // 2 - 3)

    colors = [RED, ORANGE, PINK, CYAN]
    for i, (x, y) in enumerate(level.ghost_starts):
        center = cell_center(x, y)
        pygame.draw.circle(screen, colors[i % 4], center, CELL // 2 - 4)

    text = font.render(label, True, GREEN)
    screen.blit(text, (MARGIN, 8))


def main() -> None:
    config = Parser().get_config()
    adapter = MazeAdapter(config)
    level_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    pygame.init()
    level = adapter.generate_level(level_number)
    width = MARGIN * 2 + level.width * CELL
    height = MARGIN * 2 + level.height * CELL + HUD
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pac-Man level viewer")
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    def label_for(n):
        return f"level {n}   N: next   R: regenerate   Esc: quit"

    draw_level(screen, level, font, label_for(level_number))
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_n:
                    level_number += 1
                    level = adapter.generate_level(level_number)
                elif event.key == pygame.K_r:
                    level = adapter.generate_level(level_number)
                else:
                    continue
                draw_level(screen, level, font, label_for(level_number))
                pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()