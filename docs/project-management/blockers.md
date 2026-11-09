# Blockers

- **Start-position bug:** respawn returned Pac-Man to its current cell instead of the level start. Fixed by resetting to the level's start position.
- **Edible flags never cleared:** ghosts stayed edible after the timer ended. Fixed by clearing the flags when the edible timer expires.
- **Player leaving the maze in walk-through mode:** fixed by a boundary check that still applies with the cheat on.
- **Frontend and engine crash at startup:** snapshot was called before a game started. Fixed by returning no snapshot until a level exists.
- **Frontend items:** to be filled in by the teammate.