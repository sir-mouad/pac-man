# Test plan

## Automated checks (headless tester)
- New game starts at level 1, playing, score 0, pacgums present, four ghosts
- Movement: a set direction moves Pac-Man
- Pause freezes the timer; resume restores playing
- Timer counts down
- Cheats: skip level, end game (score and victory)
- Highscores: valid name accepted, invalid name rejected

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