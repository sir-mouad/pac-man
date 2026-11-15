# Requirements

Status of each item in the subject. Done means it is implemented and checked. Partial means it works with a known gap. Deviation means the project does something different from the subject on purpose. Open means not done yet.

| Subject item | Status | Notes |
| --- | --- | --- |
| Python 3.10 or later | Done | `pyproject.toml` requires 3.13. |
| flake8 and mypy with the Makefile flags | Done | `make lint` passes. |
| Docstrings and type hints on classes and functions | Done | Added 2026-11-13. |
| Makefile: install, run, debug, clean, lint | Done | `lint-strict` (optional) is not in the Makefile. |
| `.gitignore` for Python artifacts | Done | Caches, `.venv`, `highscores.json`, `build/`, `dist/`, `mazegenerator/`. |
| Test programs (not graded) | Open | No test files are in the repository. See test-plan.md. |
| Config file is JSON with `#` comments | Done | Full-line `#` comments are ignored. |
| Bad or missing config values fall back to defaults with a message | Done | Checked 2026-11-15 with null, wrong-type, array, string and directory inputs. |
| Config can be any file name, as long as the content is JSON | Done | The parser reads the content, not the extension. |
| Exactly one configuration argument | Partial | Zero arguments uses `config.json`. A second argument prints the usage message but exits with code 0. |
| Maze generator used unmodified, `perfect=False` | Done | `engine/maze_adapter.py`. |
| Level 1 uses a fixed seed, later levels are random | Done | Level 1 uses `seed` (default 42). Later levels use seed 0, which the package treats as random. A seed of 0 or less falls back to 42. |
| At least 10 levels | Done | The default config has 11 levels. |
| Each level has a time limit; time running out ends the game | Done | `level_max_time`, default 180 seconds. The timer only counts while Pac-Man is moving (see blockers.md). |
| Four ghosts start in the corners, Pac-Man in the middle | Done | `engine/maze_adapter.py`. |
| Pacgums in most corridors, super pacgums in the corners | Done | Every open cell except corners and start has a pacgum. |
| Pac-Man has 3 lives at the start | Deviation | The default is 10 (config key `lives`). Set it to 3 to match the subject. |
| Pac-Man stops at walls and at the edge | Done | Implemented. Manual check still to do (see test-plan.md). |
| Ghosts chase, flee when edible, respawn after a while | Done | Respawn after 5 seconds. Edible for 8 seconds. |
| Scoring: pacgum, super pacgum, edible ghost | Done | Values set in config. Score never decreases. |
| Power pellets work on every level | Done | Unless `imposible_levels` is `true` (optional key, default `false`). |
| Persistent top-10 highscores | Done | JSON file named by `highscore_filename`. |
| Name: 1 to 10 letters, digits or spaces; score: non-negative integer | Done | Enforced in `engine/highscores.py`. |
| Highscores loaded at start, saved at game end | Done | Saved when the name is submitted. |
| Highscore errors do not crash the game | Done | Missing file: empty table. Invalid file: warning and empty table. Save error: warning. |
| Main menu: start, highscores, instructions, exit | Done | Exit is "Exit arcade" on the menu. |
| HUD: score, lives, level, remaining time | Done | Play screen. |
| Pause menu: resume and return to main menu | Done | P or Escape pauses. |
| Game-over and victory screens with name entry | Done | Name entry screen, then back to the menu. |
| Cheat mode for peer review | Done | Six cheats, shown on the play screen and explained in How To Play. |
| Standalone executable (PyInstaller) with config bundled | Done for Linux | `make build`. Windows and macOS builds not made. |
| Public, unlisted build on a gaming platform | Done | Itch.io, Linux build. |
| README with the subject's required sections | Done | First line italicized, sections in the subject's order. |
| Project management documents | Done | This folder. |
| MLX equivalence: every function used has an MLX equivalent | Open | Review not done. pygame is the library used. |
| Ready for a small change during the evaluation | Open | Walk through each module before the defense. |
