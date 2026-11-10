# Blockers

- **Start-position bug:** respawn returned Pac-Man to its current cell instead of the level start. Fixed by resetting to the level's start position.
- **Edible flags never cleared:** ghosts stayed edible after the timer ended. Fixed by clearing the flags when the edible timer expires.
- **Player leaving the maze in walk-through mode:** fixed by a boundary check that still applies with the cheat on.
- **Frontend and engine crash at startup:** snapshot was called before a game started. Fixed by returning no snapshot until a level exists.
- **Frontend startup:** avoided calling snapshot before a level exists by starting an engine session for the static menu preview; simulation advances only on the playing screen.
- **Resize clipping:** replaced fixed window drawing with a logical canvas, scaled letterboxing and mapped mouse hit testing.
- **Silent highscore failures:** save previously returned success even when writing failed. Save now reports errors, rolls back the entry and keeps the name form open for retry.
- **Working-directory-dependent paths:** launcher now resolves bundled config and OS user data separately; explicit config paths anchor their relative highscore filenames.
