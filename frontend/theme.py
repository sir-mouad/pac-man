"""Small, asset-free drawing primitives and a consistent arcade palette."""

import math

import pygame


SIZE = (1280, 840)
INK = (10, 16, 23)
SURFACE = (16, 25, 34)
RAISED = (23, 34, 43)
LINE = (39, 54, 63)
WHITE = (241, 242, 229)
MUTED = (141, 158, 163)
YELLOW = (255, 216, 77)
TEAL = (88, 210, 189)
BLUE = (73, 117, 243)
RED = (255, 112, 120)
GHOSTS = (RED, (244, 157, 195), (111, 216, 231), (255, 175, 105))

# Original 5 x 7 lettering; integer blocks keep the arcade wordmark crisp.
GLYPHS = {
    "P": (30, 17, 17, 30, 16, 16, 16),
    "A": (14, 17, 17, 31, 17, 17, 17),
    "C": (15, 16, 16, 16, 16, 16, 15),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 25, 21, 19, 19, 17),
    "-": (0, 0, 0, 31, 0, 0, 0),
}


class Painter:
    def __init__(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        # Pygame's redistributable bundled font, never a host-specific font.
        self.fonts = {
            size: pygame.font.Font(None, size)
            for size in (18, 20, 22, 24, 26, 28, 32, 36, 44, 54, 72, 96)
        }

    def text(self, value: object, pos: tuple[float, float], size: int = 24,
             color: tuple = WHITE, align: str = "left") -> pygame.Rect:
        image = self.fonts[size].render(str(value), True, color)
        rect = image.get_rect()
        if align == "center":
            rect.midtop = (round(pos[0]), round(pos[1]))
        elif align == "right":
            rect.topright = (round(pos[0]), round(pos[1]))
        else:
            rect.topleft = (round(pos[0]), round(pos[1]))
        self.canvas.blit(image, rect)
        return rect

    def panel(self, rect: pygame.Rect | tuple, color: tuple = SURFACE,
              border: tuple = LINE, radius: int = 18) -> None:
        pygame.draw.rect(self.canvas, color, rect, border_radius=radius)
        pygame.draw.rect(self.canvas, border, rect, 1, border_radius=radius)

    def label(self, value: str, pos: tuple, color: tuple = MUTED) -> None:
        x, y = pos
        for char in value.upper():
            image = self.fonts[18].render(char, True, color)
            self.canvas.blit(image, (x, y))
            x += image.get_width() + 2

    def wordmark(self, pos: tuple, scale: int = 4) -> None:
        x, y = pos
        for char in "PAC-MAN":
            for row, bits in enumerate(GLYPHS[char]):
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        pygame.draw.rect(self.canvas, YELLOW,
                                         (x + col * scale, y + row * scale,
                                          scale, scale))
            x += 6 * scale

    def key(self, value: str, pos: tuple, width: int = 34) -> None:
        x, y = pos
        self.panel((x, y, width, 28), RAISED, LINE, 6)
        self.text(value, (x + width / 2, y + 6), 18, WHITE, "center")

    def pacman(self, pos: tuple, radius: float, angle: float = 0,
               phase: float = 0) -> None:
        x, y = pos
        mouth = 0.16 + 0.34 * abs(math.sin(phase * 9))
        points = [(x, y)]
        for i in range(41):
            a = angle + mouth + (math.tau - 2 * mouth) * i / 40
            points.append((x + math.cos(a) * radius,
                           y + math.sin(a) * radius))
        pygame.draw.polygon(self.canvas, YELLOW, points)

    def ghost(self, pos: tuple, radius: float, color: tuple,
              edible: bool = False, phase: float = 0) -> None:
        x, y = pos
        r = max(4, round(radius))
        x, y = round(x), round(y)
        if edible:
            color = WHITE if int(phase * 4) % 6 == 0 else BLUE
        pygame.draw.circle(self.canvas, color, (x, y - r // 4), r)
        pygame.draw.rect(self.canvas, color, (x - r, y - r // 4, r * 2, r))
        wave = int(phase * 5) % 2
        points = [(x - r, y), (x + r, y), (x + r, y + r)]
        for i in range(6, -1, -1):
            points.append((x - r + i * r / 3,
                           y + r - (r / 3 if (i + wave) % 2 else 0)))
        pygame.draw.polygon(self.canvas, color, points)
        if edible:
            face = INK if color == WHITE else WHITE
            for dx in (-r // 3, r // 3):
                pygame.draw.rect(self.canvas, face,
                                 (x + dx - 1, y - r // 3, 3, 3))
            pygame.draw.lines(self.canvas, face, False,
                              [(x - r / 2 + i * r / 4,
                                y + r / 3 + (i % 2) * r / 5)
                               for i in range(5)], 2)
        else:
            for eye_offset in (-r * .38, r * .38):
                eye = (round(x + eye_offset), round(y - r * .2))
                pygame.draw.ellipse(self.canvas, WHITE,
                                    (eye[0] - r * .25, eye[1] - r * .35,
                                     r * .5, r * .7))
                pygame.draw.circle(self.canvas, INK,
                                   (eye[0] + 1, eye[1]), max(2, r // 7))

    def background(self) -> None:
        self.canvas.fill(INK)
        for x in range(24, SIZE[0], 24):
            for y in range(24, SIZE[1], 24):
                pygame.draw.circle(self.canvas, (24, 34, 41), (x, y), 1)
