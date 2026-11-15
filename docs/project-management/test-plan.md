# Test plan

## Automated
- `make lint`: flake8 with the project's rules, and mypy with the Makefile's flags. Passes on the current code.
- The repository has no test files and no `make test` target.

## Checks done during development
These were run by hand or with short scripts. They are not in the repository.
- **13-11-2026:** flake8 and mypy after the lint and type fixes. For each changed file, the syntax tree was compared before and after, ignoring annotations, docstrings and imports. This confirmed no logic changed.
- **15-11-2026, config:** the parser was run on a missing file, a directory, an empty file, a JSON array, a JSON string, `{"lives": null}`, `{"lives": [1]}`, `{"levels": 5}`, `{"levels": [5]}`, `{"levels": [{"width": null, "height": 3}]}`, `{"lives": "abc"}`, `{"seed": 0}`, unterminated JSON, and a trailing comma. Every case either loaded or fell back to the defaults.
- **15-11-2026, highscores:** a name of empty text is rejected without an error.
- **15-11-2026, ghosts:** after three power pellets, the ghost speed returns to its base value.
- **15-11-2026, screens:** the How To Play, cheat guide and play screens were rendered headlessly at 1280 x 840 and inspected.
- **13-11-2026, build:** the standalone Linux build was run from a terminal.

## Manual playtest checklist (to do on a real display)
- [ ] Pac-Man stops at walls and at the edge of the maze
- [ ] Eating a super pacgum makes ghosts blue and edible, and they return to normal speed when it ends
- [ ] A ghost that catches Pac-Man: Pac-Man returns to the start and the ghosts reset
- [ ] A ghost that Pac-Man has just eaten does not take a life for 5 seconds
- [ ] Ghosts stay still until Pac-Man moves
- [ ] Eating all pacgums starts the next level
- [ ] Losing all lives shows the game-over screen and the name entry
- [ ] Time running out shows the game-over screen
- [ ] A saved score appears in the top 10 and is still there after a restart
- [ ] Each cheat works as the cheat guide says
- [ ] Pause and resume with P and Escape; losing window focus pauses the game
- [ ] The packaged build works started from another folder, with and without a config argument

## Bugs
See blockers.md for the list of bugs found and their status.
