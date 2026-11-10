# Test plan

## Automated checks (headless tester)
- New game starts at level 1, playing, score 0, pacgums present, four ghosts
- Movement: a set direction moves Pac-Man
- Pause freezes the timer; resume restores playing
- Timer counts down
- Cheats: skip level, end game (score and victory)
- Highscores: valid name accepted, invalid name rejected

## Frontend integration suite (2026-11-10)
Run `make test` (14 tests, real engine, dummy SDL video/audio).

- Main menu wrapping, keyboard routes, all arrow/WASD direction mappings
- Pausing freezes the complete snapshot; resuming advances time
- Losing focus pauses; returning to the menu and starting resets the game
- Victory and game-over transitions, saving and skipping name entry
- Empty, unsupported and overlong name errors, Backspace, successful score reload
- Failed disk replacement leaves the entry screen open, removes temporary files and permits retry
- Top-10 ordering and persistence after restart
- Resized/letterboxed mouse hit testing, all screens with a portrait maze
- Large frame deltas are bounded; window close exits
- Default config, user config and explicit score paths; launch from another directory

## Build and visual checks (2026-11-10)
- `make lint`: frontend/script/test flake8 and frontend mypy
- Render and inspect menu, gameplay, pause, instructions, highscores and result screens at 1280 x 840
- `make build`: macOS arm64 PyInstaller app and standalone folder
- `make check-build`: copy the bundle outside the source tree and launch from another directory with bundled and explicit config; verify maze and score paths without a Python environment
- Still manual: sustained interactive gameplay on a real display, IME behavior, and Windows/Linux builds on their own hosts

## Manual checks
- Pac-Man stops at walls and at the maze edge
- Super-pacgum makes ghosts edible, then they return to normal
- Caught by a ghost: Pac-Man returns to start, ghosts reset
- Respawned ghost cannot catch Pac-Man for the grace period
- Ghosts hold still until Pac-Man moves
- Clearing all pacgums starts the next level
- Losing all lives ends the game
- Each cheat works as described

## Bugs found and fixed
See blockers.md for the list.
