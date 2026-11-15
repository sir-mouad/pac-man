# Blockers

## Resolved
- **Start-position bug:** after a life was lost, Pac-Man returned to the cell where it was caught instead of the level start. Fixed by resetting to the level start.
- **Edible flags never cleared:** ghosts stayed edible after the effect ended. Fixed by clearing the flags when the effect ends.
- **Leaving the maze in walk-through mode:** Pac-Man could leave the maze with the no-clip cheat. Fixed by a boundary check that still applies with the cheat on.
- **Startup crash:** the frontend asked for a snapshot before a level existed. Fixed by returning no snapshot until a level exists.
- **Resize clipping:** drawing now uses a fixed 1280 x 840 canvas, scaled to the window.
- **Highscore folder missing (packaged build):** saving failed because the folder did not exist. Fixed by creating the folder before the first save.
- **Root-owned highscore file:** commands run with `sudo` left `highscores.json` owned by root with mode 000. Fixed by restoring ownership. Do not use `sudo` for project commands.
- **`make build` reported "up to date":** a folder with the same name as the target. Fixed with `.PHONY: build`.
- **Config crashes:** null values, lists, a non-object JSON value and wrong types crashed the game. Fixed in the 14-11-2026 parser changes and checked on 15-11-2026.
- **Crash on an invalid name:** the name screen read an error field that was never set. Fixed by removing the field (14-11-2026).
- **Ghost speed build-up:** each power pellet made the ghosts slower, and the speed was never reset. Fixed: the speed returns to the base value when the effect ends. Checked on 15-11-2026.

## Open
- **Level timer counts only while Pac-Man moves.** `engine/engine.py` updates the timer only when the player has a direction. Decide whether this is intended.
- **Protection and respawn overlap.** A ghost that Pac-Man eats is protected for 5 seconds, and it respawns after a 5-second wait. Both start at the same moment, so the ghost has no protection after it respawns.
- **Lives default is 10.** The subject's example uses 3.
- **Highscore path depends on the start folder.** See decisions.md.
- **Wrong message for a directory.** A directory passed as the config prints "not found". The file still falls back to the defaults.
- **Two arguments exit with code 0.** `python pac-man.py a b` prints the usage message but exits with code 0.
- **MLX equivalence review** is not done.
- **Windows and macOS builds** are not made.
- **Interactive playtesting** on a real display is not done (see test-plan.md).
