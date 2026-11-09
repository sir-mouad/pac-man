import pygame

from engine.engine import GameEngine
from engine.shared import State, Direction


CELL = 30
PADDING = 28
HUD = 100
FOOTER = 42
FPS = 60

WIDTH = 760
HEIGHT = 560

BACKGROUND = (8, 12, 28)
PANEL = (17, 25, 48)
PANEL_LIGHT = (25, 36, 65)
BLUE = (45, 110, 255)
BLUE_LIGHT = (90, 160, 255)
WHITE = (240, 245, 255)
MUTED = (130, 145, 175)
YELLOW = (255, 220, 50)
PINK = (255, 100, 180)
RED = (255, 75, 90)
CYAN = (50, 220, 255)
ORANGE = (255, 165, 65)
GREEN = (70, 230, 150)
GRAY = (120, 130, 150)

GHOST_COLORS = [RED, PINK, CYAN, ORANGE]

KEY_TO_DIRECTION = {
    pygame.K_UP: Direction.UP,
    pygame.K_w: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_a: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_d: Direction.RIGHT,
}


def get_fonts():
    return {
        "title": pygame.font.SysFont("arial", 58, bold=True),
        "heading": pygame.font.SysFont("arial", 30, bold=True),
        "large": pygame.font.SysFont("arial", 25, bold=True),
        "normal": pygame.font.SysFont("arial", 19),
        "small": pygame.font.SysFont("arial", 15),
        "tiny": pygame.font.SysFont("arial", 13),
    }


def draw_text(surface, text, font, color, position, center=False):
    rendered = font.render(str(text), True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = position
    else:
        rect.topleft = position

    surface.blit(rendered, rect)
    return rect


def draw_panel(surface, rect, color=PANEL, radius=16):
    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=radius
    )


def draw_background(surface):
    surface.fill(BACKGROUND)

    for x in range(0, WIDTH, 40):
        for y in range(0, HEIGHT, 40):
            pygame.draw.circle(
                surface,
                (18, 26, 47),
                (x, y),
                1
            )


def draw_button(surface, rect, text, font, selected=False):
    color = BLUE if selected else PANEL_LIGHT

    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        surface,
        BLUE_LIGHT if selected else (40, 55, 85),
        rect,
        1,
        border_radius=12
    )

    draw_text(
        surface,
        text,
        font,
        WHITE,
        rect.center,
        center=True
    )


def cell_center(x, y):
    return (
        PADDING + x * CELL + CELL // 2,
        PADDING + y * CELL + CELL // 2 + HUD
    )


def draw_maze(surface, snap):
    for y in range(snap.height):
        for x in range(snap.width):
            north, east, south, west = snap.walls[y][x]

            left = PADDING + x * CELL
            top = PADDING + y * CELL + HUD

            right = left + CELL
            bottom = top + CELL

            if north:
                pygame.draw.line(
                    surface, BLUE,
                    (left, top), (right, top), 3
                )

            if east:
                pygame.draw.line(
                    surface, BLUE,
                    (right, top), (right, bottom), 3
                )

            if south:
                pygame.draw.line(
                    surface, BLUE,
                    (left, bottom), (right, bottom), 3
                )

            if west:
                pygame.draw.line(
                    surface, BLUE,
                    (left, top), (left, bottom), 3
                )


def draw_pacman(surface, position):
    x, y = position
    radius = CELL // 2 - 3

    pygame.draw.circle(
        surface,
        YELLOW,
        (x, y),
        radius
    )

    pygame.draw.polygon(
        surface,
        BACKGROUND,
        [
            (x, y),
            (x + radius, y - radius // 2),
            (x + radius, y + radius // 2)
        ]
    )


def draw_ghost(surface, position, color, edible=False):
    x, y = position
    radius = CELL // 2 - 4

    if edible:
        color = (85, 100, 220)

    pygame.draw.circle(
        surface,
        color,
        (x, y - 3),
        radius
    )

    pygame.draw.rect(
        surface,
        color,
        (x - radius, y - 3, radius * 2, radius + 5)
    )

    pygame.draw.polygon(
        surface,
        color,
        [
            (x - radius, y + radius),
            (x - radius // 2, y + radius - 4),
            (x, y + radius),
            (x + radius // 2, y + radius - 4),
            (x + radius, y + radius),
        ]
    )

    eye_offset = 5
    eye_y = y - 5

    for offset in (-eye_offset, eye_offset):
        pygame.draw.circle(
            surface,
            WHITE,
            (x + offset, eye_y),
            4
        )

        pygame.draw.circle(
            surface,
            (20, 35, 75),
            (x + offset + 1, eye_y),
            2
        )


def draw_hud(surface, fonts, snap):
    draw_panel(
        surface,
        pygame.Rect(20, 16, WIDTH - 40, 72)
    )

    section_width = (WIDTH - 80) // 4

    stats = [
        ("SCORE", snap.score, YELLOW),
        ("LEVEL", snap.level, CYAN),
        ("LIVES", snap.lives, RED),
        ("TIME", f"{int(snap.time_left)}s", GREEN),
    ]

    for i, (label, value, color) in enumerate(stats):
        x = 42 + i * section_width

        draw_text(
            surface, label,
            fonts["tiny"], MUTED, (x, 30)
        )

        if label == "LIVES":
            for life in range(snap.lives):
                pygame.draw.circle(
                    surface,
                    YELLOW,
                    (x + 12 + life * 25, 65),
                    9
                )

        else:
            draw_text(
                surface, value,
                fonts["large"], color, (x, 49)
            )

    # if snap.message:
    #     draw_text(
    #         surface,
    #         snap.message,
    #         fonts["small"],
    #         WHITE,
    #         (PADDING, HEIGHT - 30)
    #     )


def draw_game(surface, fonts, snap):
    draw_background(surface)

    draw_hud(surface, fonts, snap)

    maze_width = snap.width * CELL
    maze_height = snap.height * CELL

    maze_rect = pygame.Rect(
        PADDING - 8,
        HUD + PADDING - 8,
        maze_width + 16,
        maze_height + 16
    )

    draw_panel(
        surface,
        maze_rect,
        (10, 16, 35),
        12
    )

    draw_maze(surface, snap)

    for x, y in snap.pacgums:
        pygame.draw.circle(
            surface,
            PINK,
            cell_center(x, y),
            3
        )

    for x, y in snap.super_pacgums:
        pygame.draw.circle(
            surface,
            WHITE,
            cell_center(x, y),
            7
        )

    for i, ghost in enumerate(snap.ghosts):
        color = GHOST_COLORS[i % len(GHOST_COLORS)]

        draw_ghost(
            surface,
            cell_center(*ghost.position),
            color,
            ghost.edible
        )

    draw_pacman(
        surface,
        cell_center(*snap.player)
    )

    draw_text(
        surface,
        "WASD / ARROWS  MOVE       P  PAUSE       ESC  QUIT",
        fonts["tiny"],
        MUTED,
        (PADDING, HEIGHT - 25)
    )


def draw_menu(surface, fonts):
    draw_background(surface)

    draw_text(
        surface,
        "PAC-MAN",
        fonts["title"],
        YELLOW,
        (WIDTH // 2, 125),
        center=True
    )

    draw_text(
        surface,
        "CLASSIC ARCADE EXPERIENCE",
        fonts["small"],
        BLUE_LIGHT,
        (WIDTH // 2, 177),
        center=True
    )

    draw_panel(
        surface,
        pygame.Rect(170, 225, 420, 190)
    )

    draw_text(
        surface,
        "READY TO PLAY?",
        fonts["heading"],
        WHITE,
        (WIDTH // 2, 270),
        center=True
    )

    draw_button(
        surface,
        pygame.Rect(260, 315, 240, 52),
        "PRESS ENTER TO START",
        fonts["normal"],
        True
    )

    draw_text(
        surface,
        "ARROWS / WASD TO MOVE",
        fonts["small"],
        MUTED,
        (WIDTH // 2, 460),
        center=True
    )

    draw_text(
        surface,
        "ESC TO EXIT",
        fonts["tiny"],
        MUTED,
        (WIDTH // 2, 490),
        center=True
    )


def draw_overlay(surface, fonts, title, subtitle, color):
    overlay = pygame.Surface(
        surface.get_size(),
        pygame.SRCALPHA
    )

    overlay.fill((3, 6, 18, 210))
    surface.blit(overlay, (0, 0))

    draw_panel(
        surface,
        pygame.Rect(130, 185, WIDTH - 260, 190),
        PANEL
    )

    draw_text(
        surface,
        title,
        fonts["heading"],
        color,
        (WIDTH // 2, 245),
        center=True
    )

    draw_text(
        surface,
        subtitle,
        fonts["normal"],
        WHITE,
        (WIDTH // 2, 295),
        center=True
    )


def draw_name_screen(surface, fonts, snap, name):
    draw_background(surface)

    draw_panel(
        surface,
        pygame.Rect(100, 145, WIDTH - 200, 270)
    )

    draw_text(
        surface,
        "GAME FINISHED",
        fonts["heading"],
        YELLOW,
        (WIDTH // 2, 200),
        center=True
    )

    draw_text(
        surface,
        f"FINAL SCORE: {snap.score}",
        fonts["large"],
        WHITE,
        (WIDTH // 2, 250),
        center=True
    )

    draw_text(
        surface,
        "ENTER YOUR NAME",
        fonts["small"],
        MUTED,
        (WIDTH // 2, 295),
        center=True
    )

    input_rect = pygame.Rect(
        205, 320, 350, 48
    )

    pygame.draw.rect(
        surface,
        (9, 16, 34),
        input_rect,
        border_radius=10
    )

    pygame.draw.rect(
        surface,
        BLUE,
        input_rect,
        2,
        border_radius=10
    )

    draw_text(
        surface,
        name + "_",
        fonts["normal"],
        WHITE,
        (input_rect.x + 15, input_rect.y + 13)
    )

    draw_text(
        surface,
        "MAX 10 CHARACTERS  |  LETTERS AND NUMBERS",
        fonts["tiny"],
        MUTED,
        (WIDTH // 2, 390),
        center=True
    )

    draw_text(
        surface,
        "PRESS ENTER TO SAVE",
        fonts["small"],
        GREEN,
        (WIDTH // 2, 450),
        center=True
    )


def main_menu(screen, fonts, clock):
    while True:
        draw_menu(screen, fonts)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True

                if event.key == pygame.K_ESCAPE:
                    return False

        clock.tick(FPS)


def ask_name(screen, fonts, clock, snap):
    name = ""

    while True:
        draw_name_screen(screen, fonts, snap, name)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip():
                        return name.strip()

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                elif event.unicode:
                    if len(name) < 10:
                        if event.unicode.isalnum() or event.unicode == " ":
                            name += event.unicode

        clock.tick(FPS)


def run():
    pygame.init()

    engine = GameEngine()

    fonts = get_fonts()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.RESIZABLE
    )

    pygame.display.set_caption("PAC-MAN | Arcade")

    if not main_menu(screen, fonts, clock):
        pygame.quit()
        return

    engine.start_new_game()

    snap = engine.snapshot()

    maze_width = PADDING * 2 + snap.width * CELL
    maze_height = HUD + snap.height * CELL + PADDING + FOOTER

    screen = pygame.display.set_mode(
        (maze_width, maze_height),
        pygame.RESIZABLE
    )

    running = True
    paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_p:
                    if snap.state == State.PLAYING:
                        engine.pause_game()
                        paused = not paused

                    if snap.state == State.PAUSED:
                        engine.pause_game()
                        paused = not paused

                elif not paused and event.key in (
                    pygame.K_1, pygame.K_2, pygame.K_3,
                    pygame.K_4, pygame.K_5
                ):
                    cheats = {
                        pygame.K_1: "skip_level",
                        pygame.K_2: "walk_through_walls",
                        pygame.K_3: "all_super",
                        pygame.K_4: "invincible",
                        pygame.K_5: "end_game",
                    }
                    engine.cheat(cheats[event.key])

                elif event.key in KEY_TO_DIRECTION and not paused:
                    engine.set_direction(
                        KEY_TO_DIRECTION[event.key]
                    )

        dt = clock.tick(FPS) / 1000.0

        if not paused:
            engine.update(dt)

        snap = engine.snapshot()

        draw_game(screen, fonts, snap)

        if paused:
            draw_overlay(
                screen,
                fonts,
                "GAME PAUSED",
                "PRESS P TO RESUME",
                YELLOW
            )

        pygame.display.flip()

        if snap.state in (State.GAME_OVER, State.VICTORY):
            draw_overlay(
                screen,
                fonts,
                "VICTORY!" if snap.state == State.VICTORY else "GAME OVER",
                f"FINAL SCORE: {snap.score}",
                GREEN if snap.state == State.VICTORY else RED
            )
            pygame.display.flip()

            pygame.time.wait(1200)

            name = ask_name(screen, fonts, clock, snap)

            if name is not None:
                engine.submit_name(name)

            running = False

    pygame.quit()


if __name__ == "__main__":

    run()
