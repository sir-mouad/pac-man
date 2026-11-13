"""One event loop for menus, gameplay, text entry, and window management."""

from enum import Enum, auto
import math
from pathlib import Path
import re

import pygame

from engine.engine import GameEngine
from engine.shared import Direction, State, Cheat
from frontend.maze import MazeRenderer
from frontend.theme import (
    GHOSTS, INK, LINE, MUTED, RAISED, RED, SIZE, SURFACE, TEAL, WHITE,
    YELLOW, Painter,
)


FPS = 60
STEP = 1 / FPS
KEY_DIRECTIONS = {
    pygame.K_UP: Direction.UP, pygame.K_w: Direction.UP,
    pygame.K_DOWN: Direction.DOWN, pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT, pygame.K_a: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT, pygame.K_d: Direction.RIGHT,
}

KEY_CHEAT = {
    pygame.K_1: Cheat.SKIP,
    pygame.K_2: Cheat.NOCLIP,
    pygame.K_3: Cheat.SUPER,
    pygame.K_4: Cheat.Immortal,
    pygame.K_5: Cheat.AutoWin,
    pygame.K_6: Cheat.Reset
}


class Screen(Enum):
    """Screens the application can show."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    SCORES = auto()
    INSTRUCTIONS = auto()
    RESULT = auto()


class Application:
    """Runs the window, event loop, menus, and in-game screens."""
    def __init__(self, engine: GameEngine) -> None:
        """Open the window and show the main menu."""
        pygame.display.init()
        pygame.font.init()
        self.engine = engine
        self.canvas = pygame.Surface(SIZE)
        desktop = pygame.display.get_desktop_sizes()[0]
        scale = min(1, (desktop[0] - 80) / SIZE[0],
                    (desktop[1] - 100) / SIZE[1])
        scale = max(.5, scale)
        self.window = pygame.display.set_mode(
            (round(SIZE[0] * scale), round(SIZE[1] * scale)), pygame.RESIZABLE)
        pygame.display.set_caption("PAC-MAN / One more round")
        self.p = Painter(self.canvas)
        icon = pygame.Surface((48, 48))
        icon.fill(INK)
        Painter(icon).pacman((24, 24), 20, phase=.12)
        pygame.display.set_icon(icon)
        self.maze = MazeRenderer(self.p)
        self.clock = pygame.time.Clock()
        self.running = True
        self.screen = Screen.MENU
        self.selected = 0
        self.phase = 0.0
        self.game_phase = 0.0
        self.accumulator = 0.0
        self.name = ""
        self.error = ""
        self.notice = ""
        self.notice_time = 0.0
        self.buttons: list[tuple[pygame.Rect, str, bool]] = []
        self.focus_actions: list[str] = []
        self.viewport = pygame.Rect((0, 0), SIZE)
        # Start without advancing: a real engine snapshot doubles as the
        # attract screen. No rules or maze layout are duplicated in the UI.
        self.engine.start_new_game()
        self.snapshot = self.engine.snapshot()
        self.preview = self.snapshot
        pygame.key.stop_text_input()
        self.draw()

    def navigate(self, screen: Screen) -> None:
        """Switch to a screen and reset its selection."""
        self.screen = screen
        self.selected = 0
        self.accumulator = 0
        if screen is Screen.RESULT:
            self.name = ""
            self.error = ""
            pygame.key.start_text_input()
        else:
            pygame.key.stop_text_input()
        self.draw()

    def start(self) -> None:
        """Start a new game and show the play screen."""
        self.engine.start_new_game()
        self.snapshot = self.engine.snapshot()
        self.game_phase = 0
        self.notice = ""
        self.navigate(Screen.PLAYING)

    def pause(self) -> None:
        """Pause the game if it is running."""
        if self.screen is Screen.PLAYING:
            self.engine.pause_game()
            self.snapshot = self.engine.snapshot()
            self.navigate(Screen.PAUSED)

    def resume(self) -> None:
        """Resume a paused game."""
        self.engine.pause_game()
        self.snapshot = self.engine.snapshot()
        self.navigate(Screen.PLAYING)

    def activate(self, action: str) -> None:
        """Run the action for a menu button or key press."""
        if action == "start":
            self.start()
        elif action == "scores":
            self.navigate(Screen.SCORES)
        elif action == "instructions":
            self.navigate(Screen.INSTRUCTIONS)
        elif action == "exit":
            self.running = False
        elif action == "menu":
            self.navigate(Screen.MENU)
        elif action == "pause":
            self.pause()
        elif action == "resume":
            self.resume()
        elif action == "save":
            if self.engine.submit_name(self.name):
                self.notice = "SCORE SAVED. READY FOR ANOTHER ROUND?"
                self.notice_time = 6
                self.navigate(Screen.MENU)
            else:
                self.error = (self.engine.highscores.last_error
                              or "Use 1-10 letters, numbers or spaces.")

    def logical_position(self, pos: tuple) -> tuple[float, float]:
        """Convert a window pixel position to canvas coordinates."""
        return ((pos[0] - self.viewport.x) * SIZE[0] / self.viewport.width,
                (pos[1] - self.viewport.y) * SIZE[1] / self.viewport.height)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Route one pygame event to the right handler."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.pause()
        elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            pos = self.logical_position(event.pos)
            for rect, action, keyboard in self.buttons:
                if rect.collidepoint(pos):
                    if keyboard:
                        self.selected = self.focus_actions.index(action)
                    if (event.type == pygame.MOUSEBUTTONDOWN
                            and event.button == 1):
                        self.activate(action)
                    break
        elif event.type == pygame.TEXTINPUT and self.screen is Screen.RESULT:
            candidate = self.name + event.text
            if len(candidate) > 10:
                self.error = "Keep your name to 10 characters or fewer."
            elif re.fullmatch(r"[A-Za-z0-9 ]*", candidate) is None:
                self.error = "Use English letters, numbers and spaces only."
            else:
                self.name = candidate
                self.error = ""
        elif event.type == pygame.KEYDOWN:
            self.handle_key(event.key)

    def handle_key(self, key: int) -> None:
        """Handle a key press for the current screen."""
        if self.screen is Screen.PLAYING:
            if key in KEY_DIRECTIONS:
                self.engine.set_direction(KEY_DIRECTIONS[key])
            elif key in (pygame.K_p, pygame.K_ESCAPE):
                self.pause()
            elif key in KEY_CHEAT:
                self.engine.cheat(KEY_CHEAT[key])
            return
        if self.screen is Screen.RESULT:
            if key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
                self.error = ""
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.activate("save")
            elif key == pygame.K_ESCAPE:
                self.activate("menu")
            return
        if self.screen is Screen.PAUSED and key in (
                pygame.K_p, pygame.K_ESCAPE):
            self.resume()
            return
        if key == pygame.K_ESCAPE:
            self.activate("exit" if self.screen is Screen.MENU else "menu")
            return
        if self.focus_actions:
            if key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(self.focus_actions)
            elif key in (pygame.K_DOWN, pygame.K_s, pygame.K_TAB,
                         pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(self.focus_actions)
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.activate(self.focus_actions[self.selected])

    def update(self, elapsed: float) -> None:
        """Advance animations and, during play, the game."""
        elapsed = max(0, min(elapsed, .1))
        self.phase += elapsed
        self.notice_time = max(0, self.notice_time - elapsed)
        if self.screen is not Screen.PLAYING:
            return
        self.game_phase += elapsed
        self.accumulator += elapsed
        while self.accumulator >= STEP:
            self.engine.update(STEP)
            self.accumulator -= STEP
            self.snapshot = self.engine.snapshot()
            if self.snapshot.state in (State.GAME_OVER, State.VICTORY):
                self.navigate(Screen.RESULT)
                break
            if self.snapshot.state is State.PAUSED:
                self.navigate(Screen.PAUSED)
                break

    def button(self, rect: tuple, label: str, action: str,
               primary: bool = False, keyboard: bool = True,
               number: str = "") -> None:
        """Draw a menu button and register it for mouse and keyboard."""
        index = len(self.focus_actions)
        if keyboard:
            self.focus_actions.append(action)
        self.buttons.append((pygame.Rect(rect), action, keyboard))
        focused = keyboard and index == self.selected
        color = YELLOW if primary else (RAISED if focused else SURFACE)
        self.p.panel(rect, color, YELLOW if focused else LINE, 10)
        x, y, w, h = rect
        text_color = INK if primary else (YELLOW if focused else WHITE)
        if number:
            self.p.text(number, (x + 20, y + h / 2 - 8), 20,
                        INK if primary else MUTED)
        self.p.text(label, (x + (56 if number else 20), y + h / 2 - 11),
                    28 if h > 45 else 22, text_color)
        self.p.text(">" if focused or primary else "+",
                    (x + w - 22, y + h / 2 - 10), 26, text_color, "right")

    def header(self, active: str = "LOBBY") -> None:
        """Draw the top bar with the logo and section name."""
        self.p.pacman((55, 48), 15, phase=.14)
        self.p.wordmark((83, 37), 3)
        pygame.draw.line(self.canvas, LINE, (231, 34), (231, 62))
        self.p.label("ARCADE CLUB", (251, 42))
        self.p.label(active, (1044, 42), TEAL)
        pygame.draw.circle(self.canvas, TEAL, (1217, 48), 4)
        pygame.draw.line(self.canvas, LINE, (40, 88), (1240, 88))

    def footer(
        self,
        message: str = "A LITTLE NOSTALGIA. A NEW HIGH SCORE.",
    ) -> None:
        """Draw the bottom bar with a short message."""
        pygame.draw.line(self.canvas, LINE, (40, 785), (1240, 785))
        self.p.label("42 / PAC-MAN", (42, 806))
        self.p.text(message, (1240, 806), 18, MUTED, "right")

    def draw_menu(self) -> None:
        """Draw the main menu with the attract-mode maze preview."""
        self.header()
        self.p.label("THE CLASSIC. YOUR NEXT CHALLENGE.", (56, 133), TEAL)
        self.p.text("One more", (51, 178), 96)
        self.p.text("round.", (51, 260), 96, YELLOW)
        self.p.text("Chase dots. Dodge ghosts. Beat your best.",
                    (56, 362), 26, MUTED)
        self.p.text("Some things never get old.", (56, 393), 26, MUTED)
        items = [("Start game", "start"), ("View highscores", "scores"),
                 ("How to play", "instructions"), ("Exit arcade", "exit")]
        for i, (label, action) in enumerate(items):
            self.button((56, 454 + i * 62, 410, 52), label, action,
                        primary=i == 0, number=f"0{i + 1}")
        self.p.key("W/S", (56, 726), 44)
        self.p.text("or arrows to select", (110, 732), 20, MUTED)
        self.p.key("ENTER", (281, 726), 62)
        self.p.text("to play", (353, 732), 20, MUTED)

        self.p.panel((522, 124, 702, 571), INK, LINE, 22)
        self.p.label("THE MAZE IS CALLING", (548, 150))
        self.p.label(f"LEVEL {self.preview.level:02d}", (1102, 150), TEAL)
        self.maze.draw(self.preview, pygame.Rect(548, 193, 650, 456),
                       self.phase)
        self.p.text("ALL DOTS. NO SHORTCUTS.", (873, 666), 18, MUTED,
                    "center")
        self.p.panel((522, 710, 702, 50), SURFACE, LINE, 10)
        self.p.label("MEET THE LOCALS", (542, 729))
        for i, (name, color) in enumerate(zip(
                ("BLINKY", "PINKY", "INKY", "CLYDE"), GHOSTS)):
            x = 763 + i * 111
            self.p.ghost((x, 735), 10, color, phase=self.phase)
            self.p.text(name, (x + 16, 729), 18, MUTED)
        if self.notice and self.notice_time > 0:
            self.footer(self.notice)
        else:
            self.footer()

    def draw_game(self) -> None:
        """Draw the play screen: score, timer, lives, and maze."""
        snap = self.snapshot
        self.header(
            "IN THE MAZE" if self.screen is Screen.PLAYING else "PAUSED")
        self.p.label(f"LEVEL {snap.level:02d}", (42, 118), TEAL)
        self.p.text("Make every", (40, 154), 44)
        self.p.text("dot count.", (40, 194), 44, YELLOW)
        self.p.panel((40, 265, 245, 116))
        self.p.label("YOUR SCORE", (62, 285))
        score = f"{snap.score:06d}"
        self.p.text(score, (62, 315), 54 if len(score) < 10 else 28, YELLOW)
        self.p.panel((40, 395, 245, 102))
        self.p.label("TIME LEFT", (62, 415))
        seconds = max(0, math.ceil(snap.time_left))
        self.p.text(f"{seconds // 60:02d}:{seconds % 60:02d}",
                    (62, 445), 44, RED if seconds <= 30 else WHITE)
        self.p.label("LIVES", (42, 526))
        for i in range(min(max(0, snap.lives), 5)):
            self.p.pacman((57 + i * 35, 571), 11, phase=.12)
        self.p.text(f"x {snap.lives}", (246, 563), 24, MUTED, "right")
        self.p.label("THE MISSION", (42, 624))
        self.p.text("Clear the maze.", (42, 653), 24, WHITE)
        self.p.text("Keep the ghosts guessing.", (42, 681), 22, MUTED)
        self.button((40, 724, 245, 38), "Pause  [P]", "pause",
                    keyboard=False)
        self.p.panel((311, 115, 929, 647), INK, LINE, 20)
        self.maze.draw(snap, pygame.Rect(334, 139, 883, 570),
                       self.game_phase)
        self.p.label("ARROWS / WASD   MOVE", (340, 735))
        if snap.player_direction is None:
            self.p.text("PICK A DIRECTION TO BEGIN", (1213, 735), 18,
                        YELLOW, "right")
        else:
            self.p.text("POWER PELLET = EDIBLE GHOSTS", (1213, 735), 18,
                        MUTED, "right")
        self.footer("P / ESC   PAUSE       •       TAKE IT ONE DOT AT A TIME")

    def draw_pause(self) -> None:
        """Draw the game behind a dimmed pause menu."""
        self.draw_game()
        self.buttons = []
        self.focus_actions = []
        shade = pygame.Surface(SIZE, pygame.SRCALPHA)
        shade.fill((5, 10, 16, 215))
        self.canvas.blit(shade, (0, 0))
        self.p.panel((390, 219, 500, 398), SURFACE, LINE, 24)
        self.p.label("TAKE A BREATHER", (640 - 87, 254), TEAL)
        self.p.text("Round on hold.", (640, 296), 54, WHITE, "center")
        self.p.text("Your dots will be right here.", (640, 357), 26,
                    MUTED, "center")
        self.button((432, 416, 416, 58), "Resume game", "resume", True)
        self.button((432, 489, 416, 52), "Back to main menu", "menu")
        self.p.text("P or ESC to jump back in", (640, 574), 20, MUTED,
                    "center")

    def page_title(self, eyebrow: str, title: str, subtitle: str) -> None:
        """Draw the heading shared by the score and help pages."""
        self.header(eyebrow)
        self.p.label(eyebrow, (80, 132), TEAL)
        self.p.text(title, (77, 170), 72)
        self.p.text(subtitle, (80, 246), 26, MUTED)

    def draw_scores(self) -> None:
        """Draw the highscore table."""
        self.page_title("HALL OF FAME", "Good runs. Great players.",
                        "Ten spots. A whole lot of bragging rights.")
        self.p.panel((80, 301, 1120, 385))
        self.p.label("RANK", (109, 322))
        self.p.label("PLAYER", (220, 322))
        self.p.label("SCORE", (1090, 322))
        entries = self.engine.highscores.top(10)
        if not entries:
            self.p.pacman((640, 434), 29, phase=self.phase)
            self.p.text("The first spot has your name on it.", (640, 499),
                        36, WHITE, "center")
            self.p.text("Play a round and make arcade history.", (640, 542),
                        26, MUTED, "center")
        for i, entry in enumerate(entries):
            y = 359 + i * 31
            if i % 2 == 0:
                pygame.draw.rect(self.canvas, RAISED,
                                 (96, y - 3, 1088, 31), border_radius=5)
            color = YELLOW if i == 0 else WHITE
            self.p.text(f"{i + 1:02d}", (111, y), 24, color)
            self.p.text(entry["name"], (220, y), 26, color)
            self.p.text(f'{entry["score"]:,}', (1158, y), 26, color, "right")
        self.button((80, 713, 300, 50), "Back to main menu", "menu")
        self.button((916, 713, 284, 50), "Chase a high score", "start", True)
        self.footer(
            "UP / DOWN   SELECT       ENTER   CONFIRM       ESC   BACK")

    def draw_instructions(self) -> None:
        """Draw the how-to-play page."""
        self.page_title("HOW TO PLAY", "A classic for a reason.",
                        "Easy to pick up. One more round to master.")
        cards = [
            (80, "01", "Find your rhythm.",
             ("Use the arrow keys or WASD to move.",
              "Your next turn is buffered until it is possible.",
              "Press P or Escape to pause and resume.")),
            (652, "02", "Small dots. Big plans.",
             ("Eat every dot and power pellet to clear a level.",
              "Power pellets make ghosts blue and edible.",
              "Catch them while you have the upper hand.")),
        ]
        for x, number, title, lines in cards:
            self.p.panel((x, 308, 548, 215))
            self.p.label(number, (x + 25, 333), TEAL)
            self.p.text(title, (x + 25, 365), 36)
            for i, line in enumerate(lines):
                self.p.text(line, (x + 25, 416 + i * 29), 24, MUTED)
        self.p.panel((80, 544, 1120, 138))
        self.p.label("03", (105, 569), TEAL)
        self.p.text("Stay in the game.", (105, 599), 36)
        for i, line in enumerate((
                "Avoid ghosts. Your round ends when lives or time run out.",
                "Clear all levels to win. "
                "Save your score with your arcade name.",
                "Names use 1-10 English letters, numbers or spaces.")):
            self.p.text(line, (449, 565 + i * 32), 24, MUTED)
        self.button((80, 713, 300, 50), "Back to main menu", "menu")
        self.button((916, 713, 284, 50), "Let's play", "start", True)
        self.footer(
            "ARROWS / WASD   MOVE       P / ESC   PAUSE       ENTER   CONFIRM")

    def draw_result(self) -> None:
        """Draw the game-over or victory screen with the name box."""
        victory = self.snapshot.state is State.VICTORY
        self.header("ROUND COMPLETE")
        self.p.panel((270, 124, 740, 631), SURFACE, LINE, 24)
        if victory:
            for i, color in enumerate(GHOSTS):
                self.p.ghost((568 + i * 48, 187), 15, color,
                             True, self.phase)
        else:
            self.p.pacman((640, 187), 27, phase=self.phase)
        self.p.label(
            "VICTORY / ALL LEVELS CLEARED" if victory else "GAME OVER",
            (489 if victory else 588, 242), TEAL)
        self.p.text("You owned the maze." if victory else "What a run.",
                    (640, 279), 54, WHITE, "center")
        self.p.label("FINAL SCORE", (577, 351))
        self.p.text(f"{self.snapshot.score:,}", (640, 380),
                    72 if self.snapshot.score < 10**10 else 44,
                    YELLOW, "center")
        self.p.label("PUT YOUR NAME ON IT", (358, 476))
        self.p.text(f"{len(self.name)}/10", (922, 475), 20, MUTED, "right")
        self.p.panel((358, 503, 564, 60), INK, YELLOW, 10)
        cursor = "|" if int(self.phase * 2) % 2 == 0 else ""
        self.p.text(self.name + cursor if self.name else "Your arcade name" +
                    cursor, (378, 522), 32, WHITE if self.name else MUTED)
        self.p.text(
            self.error or "Letters, numbers and spaces. Make it yours.",
            (358, 577), 22, RED if self.error else MUTED)
        self.button((358, 626, 564, 54), "Save score & return", "save", True)
        self.p.text("ESC to return without saving", (640, 707), 20,
                    MUTED, "center")
        self.footer(
            "ENTER   SAVE SCORE       BACKSPACE   EDIT       ESC   SKIP")

    def draw(self) -> None:
        """Clear the frame and draw the current screen."""
        self.buttons = []
        self.focus_actions = []
        self.p.background()
        renderers = {
            Screen.MENU: self.draw_menu, Screen.PLAYING: self.draw_game,
            Screen.PAUSED: self.draw_pause, Screen.SCORES: self.draw_scores,
            Screen.INSTRUCTIONS: self.draw_instructions,
            Screen.RESULT: self.draw_result,
        }
        renderers[self.screen]()

    def present(self) -> None:
        """Scale the canvas to fit the window and show it."""
        width, height = self.window.get_size()
        scale = min(width / SIZE[0], height / SIZE[1])
        size = (max(1, round(SIZE[0] * scale)),
                max(1, round(SIZE[1] * scale)))
        self.viewport = pygame.Rect((0, 0), size)
        self.viewport.center = (width // 2, height // 2)
        self.window.fill(INK)
        if size == SIZE:
            self.window.blit(self.canvas, self.viewport)
        else:
            self.window.blit(pygame.transform.smoothscale(self.canvas, size),
                             self.viewport)
        pygame.display.flip()
        if self.screen is Screen.RESULT:
            # SDL's IME candidate window uses physical window coordinates.
            pygame.key.set_text_input_rect(pygame.Rect(
                self.viewport.x + round(358 * scale),
                self.viewport.y + round(503 * scale),
                round(564 * scale), round(60 * scale)))

    def capture(self, path: Path) -> None:
        """Save the current frame to an image file."""
        self.draw()
        path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(self.canvas, str(path))

    def run(self) -> None:
        """Run the main loop until the window is closed."""
        try:
            while self.running:
                elapsed = self.clock.tick(FPS) / 1000
                for event in pygame.event.get():
                    self.handle_event(event)
                self.update(elapsed)
                self.draw()
                self.present()
        finally:
            pygame.quit()
