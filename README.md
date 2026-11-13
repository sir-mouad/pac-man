*This project has been created as part of the 42 curriculum by mhadir, sreja.*

# Pac-Man: Ghosts! More ghosts!
![Image description](./docs/images/main-menu.png)
## Description

A playable Pac-Man game written in Python 3.13 with pygame. The player moves
Pac-Man through a maze, eats pacgums and super pacgums, avoids four ghosts,
and advances through levels until all lives or time are gone or every level is
cleared. Scores are saved to a local top-10 highscore table.

The project is split into two parts:

- `engine/` contains all game rules, maze construction, movement, ghost AI,
  scoring and highscores. It does not import pygame.
- `frontend/` draws the engine's snapshots with pygame and handles input,
  menus and the event loop.

The maze generator is the A-Maze-ing package assigned by the 42 curriculum. It
is used as provided and is not modified in this project.

## Instructions

Requirements: Python 3.13 and [uv](https://docs.astral.sh/uv/).

```sh
make install     # uv sync, then installs the mazegenerator package from the zip
make run         # starts the game with config.json from the project root
make run ARG=/absolute/path/to/config.json   # use a different config file
make lint        # flake8 and mypy
make build       # standalone executable in dist/pac-man (PyInstaller)
make clean       # removes caches
```

`make install` extracts `mazegenerator-00001.zip` and copies the `mazegenerator`
package into the project if it is not already there.

### Controls

| Action | Keys |
| --- | --- |
| Move | Arrow keys or W/A/S/D |
| Select a menu item | Up/Down, W/S or Tab |
| Confirm | Enter or Space (menu buttons also accept mouse clicks) |
| Pause / resume | P or Escape |
| Back to the menu (from the main menu, Escape exits) | Escape |
| Type a score name | Keyboard; Backspace to edit; Enter to save |
| Skip saving a score | Escape on the result screen |

### Cheat keys (for peer review)

| Key | Effect |
| --- | --- |
| 1 | Skip: clear the level's pacgums and power pellets |
| 2 | No-clip: walk through walls |
| 3 | Turn every pacgum into a super pacgum |
| 4 | Immortal: ghosts cannot cost a life |
| 5 | Auto-win: jump to the victory screen |
| 6 | Reset: undo the cheats above |

## Resources

Classic references:

- Pac-Man, history and game design: https://en.wikipedia.org/wiki/Pac-Man
- pygame documentation: https://www.pygame.org/docs/
- PyInstaller documentation: https://pyinstaller.org/en/stable/

### Use of AI

- Explaining the game logic and how the ghosts behave.

## Configuration

The game reads a JSON file. Lines starting with `#` are comments. Invalid
values print a warning and fall back to the default for that setting. Unknown
keys are ignored. A missing or unreadable file uses the defaults.

| Key | Default | Meaning |
| --- | --- | --- |
| `highscore_filename` | `"highscores.json"` | Score file name. Relative names are stored in the data directory, or beside the config file if one is given explicitly. Must end in `.json`. |
| `levels` | 20 x 15 | List of `{"width", "height"}` objects, one per level. A list shorter than 10 entries is padded with 20 x 15 levels to 11 levels in total. |
| `lives` | `10` | Lives at the start of a game. |
| `points_per_pacgum` | `10` | Points for each pacgum. |
| `points_per_super_pacgum` | `50` | Points for each super pacgum. |
| `points_per_ghost` | `200` | Points for each edible ghost eaten. |
| `seed` | `42` | Maze seed for level 1. |
| `level_max_time` | `180` | Seconds allowed per level. |

Without a config argument, the game looks for `config.json` in the user data
directory and then falls back to the copy bundled with the game, so it does not
depend on the current working directory. `PACMAN_DATA_DIR` overrides the data
directory.

## Highscore

The top 10 scores are stored in a JSON file in the user data directory:

The file has the form `{"highscores": [{"name": "...", "score": 0}]}`, sorted
from highest to lowest.

Names must be 1 to 10 letters, digits or spaces. Scores must be non-negative
integers. Invalid entries in a loaded file are skipped.

Why JSON in a plain file: it needs no database or server, it is easy to read
and debug by hand, and the Python standard library reads and writes it. A missing
file is treated as an empty table. A corrupted file prints a warning and starts
with an empty table, so the game keeps running. Save failures print a warning
and the game continues.

## Maze Generation

Levels are built by `engine/maze_adapter.py`, which calls the assigned
A-Maze-ing package as `MazeGenerator(size, perfect=False, seed=seed)`. The
`perfect=False` is set as the subject requires, for Pac-Man-style corridors.
The package returns a grid of wall bitmasks. The adapter reads bit value 1 as the
wall above the cell, 2 to its right, 4 below and 8 to its left, and stores them
as four booleans per cell in that order (up, right, down, left).

After generation, the adapter places:

- the player in the middle of the maze,
- the four ghosts in the corners,
- a super pacgum in each corner,
- a pacgum in every other open cell.

If a corner or the middle is a wall, the nearest open cell is used. Level 1 uses
the configured `seed`. Later levels use seed `0` as passed to the generator.

## Implementation

- **Game loop:** `frontend/app.py` runs at 60 FPS. Elapsed time is clamped to
  0.1 s, and the engine advances in fixed steps of 1/60 s, so the simulation
  does not depend on frame rate.
- **Movement:** Pac-Man and ghosts move one cell at a time at their own speed.
  The player's next turn is buffered until the maze allows it.
- **Ghosts:** each ghost has its own target rule. Blinky chases the player's
  cell. Pinky aims four cells ahead of the player. Inky uses Blinky's position
  to choose its target. Clyde chases while it is more than 8 cells away and
  returns to its corner when it is closer. When a power pellet is eaten, ghosts
  turn blue for 8 seconds and move away from the player. An eaten ghost waits 3
  seconds, then respawns in its corner.
- **Scoring and lives:** pacgums, power pellets and eaten ghosts add points, and
  points never decrease. A ghost touching the player costs a life unless the
  ghost is edible. Losing a life resets the player and ghosts.
- **Levels:** a level ends when all pacgums and power pellets are eaten. The
  game is won after the last level. The game is over when lives reach zero or
  the level timer runs out.
- **Pause:** P or Escape pauses. Losing window focus also pauses.
- **Rendering:** the interface is drawn at a fixed 1280 x 840 and scaled to the
  window with letterboxing. The wall layer is cached and redrawn only when the
  maze or window size changes.

## General Software Architecture

```
pac-man.py                 entry point: parses arguments, builds GameEngine and Application
engine/
  engine.py                GameEngine: owns the session, calls the other engine parts
  rules.py                 GameRules: score, lives, timers, win/lose status
  maze_adapter.py          MazeAdapter, Level: builds a level from the maze package
  movement.py              Mover (base), Player, Ghost: cell-by-cell movement
  ghosts.py                GhostAI and the four ghost target behaviors
  highscores.py            Highscores: top-10 table, validation, JSON load/save
  parser.py                Parser: reads and validates config.json, provides defaults
  shared.py                Direction, State, Cheat enums; GameSnapshot, GhostView dataclasses
frontend/
  app.py                   Application: window, event loop, menus and game screens
  maze.py                  MazeRenderer: draws the maze and sprites from a snapshot
  theme.py                 Painter: palette, text and sprite drawing primitives
  paths.py                 data_directory, default_config, score_path
```

Data flows one way. The frontend asks the engine to advance, then reads a
`GameSnapshot` (a plain copy of the state) to draw. It never changes game rules.

## Project Management

Planning, timeline, progress, risks, decisions, blockers, team roles and the
test plan are in [`docs/project-management/`](docs/project-management/README.md).
