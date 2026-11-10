# Decisions

- **Graphics library:** pygame. Checked against the MLX rule: every function used needs an MLX equivalent. [Confirm this check is complete before submission.]
- **Maze generation:** the assigned A-Maze-ing package is used unmodified, with PERFECT set to False and seed 42 for level 1.
- **Config format:** JSON with full-line `#` comments, read through a comment-stripping step. Missing or invalid values fall back to defaults and log a warning.
- **Highscores:** stored in a JSON file, top 10, names limited to 10 alphanumeric characters and spaces, scores non-negative integers.
- **Ghost behavior:** fixed targeting rules instead of random movement. Blinky targets the player, Pinky targets four cells ahead (up uses the straight rule, not the arcade left shift), Inky uses Blinky's position and the two-cell point, Clyde chases beyond 8 cells and retreats within it.
- **Ghost flee rule:** all ghosts flee the same way when edible.
- **Ghost hold:** ghosts stay still until Pac-Man has a direction, at the start of a level and after a life is lost.
- **Grace period:** a ghost that returns after eating Pac-Man can't catch Pac-Man for 2 seconds.
- **Cheats:** skip level, walk through walls (boundary still enforced), all pacgums become super-pacgums, end game with a fixed score, invincible.
- **Frontend contract:** shared types live in `engine/shared.py`, and the frontend reads only the snapshot.
- **Frontend architecture:** a single 60 FPS Pygame loop owns all screens. Engine updates run only on the playing screen, with a bounded frame delta and fixed 1/60-second steps. Visual easing follows observed snapshot cells; no game rules live in the frontend.
- **Visual direction:** dark ink panels, warm yellow actions, teal maze walls, bundled Pygame typography, and original code-drawn sprites/wordmark. No runtime downloads or platform-dependent fonts.
- **Window behavior:** a 1280 x 840 logical canvas scales to a resizable window with letterboxing; mouse coordinates are mapped back to the canvas. Losing focus pauses the engine.
- **Runtime paths:** bundled resources resolve relative to the module location. Default scores and optional user config live in the OS user data directory; explicit configs resolve relative score paths beside themselves. `PACMAN_DATA_DIR` supports portable/test installs.
- **Score writes:** write and flush a temporary file beside the score file, then atomically replace it. Failed saves roll back the in-memory entry and display an error on the name screen.
- **Packaging:** PyInstaller builds the whole desktop application, including config and Pygame fonts. Builds must be produced and validated on each target OS/architecture.
- **Ghost and super-pacgum placement:** [to confirm: shared corners or separate cells].
