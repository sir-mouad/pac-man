# Progress log

## 2026-10-15
- What was done: set up the project plan and split the work between backend (mhadir) and frontend (sreja). Read the subject and listed the mandatory items. Designed the config keys and defaults.
- What was tested: none yet.
- What is next: config parser and maze adapter.

## 2026-10-22
- What was done: wrote the config parser, with full-line comment handling, type checks, default fallback, and warnings for bad values. Wrote the maze adapter: level sizes and seeds, wall decoding from the package's numbers, placement of the player, ghosts, super-pacgums, and pacgums, and a nearest-open-cell search.
- What was tested: the parser against valid, missing, and invalid files. The maze adapter by generating levels and printing the grid.
- What is next: movement and the game rules.

## 2026-10-29
- What was done: wrote movement (the mover, player, and ghost classes, with wall checks and buffered turns). Wrote the game rules: score, lives, timer, status, and collection of pacgums and super-pacgums.
- What was tested: single-step movement and wall blocking. Rules state changes by hand.
- What is next: highscore store and the ghost AI.

## 2026-11-05
- What was done: wrote the highscore store, with validation, top 10, and safe loading. Wrote the ghost AI with fixed targeting for each ghost, the flee rule, the respawn countdown, and the hold until the player moves. Wrote the engine and its public methods, the snapshot, and the shared types file.
- What was tested: a headless tester covering start, movement, pause, timer, cheats, and name submission. Visual checks with a pygame stand-in for the frontend.
- What is next: gameplay fixes from the test runs, and integration with sreja's frontend.

## 2026-11-09
- What was done: fixed the gameplay bugs found in testing: ghosts too fast, Pac-Man not returning to start after a lost life, edible flags never cleared, a player able to leave the maze in walk-through mode, and the startup crash when no game was running. Added the grace period after a ghost respawns, and the ghost hold until Pac-Man moves.
- What was tested: each fix by running the game, and the headless tester after each change.
- What is next: finish the frontend integration with sreja, then the README and packaging.

## 2026-11-14
- What was done: wrote the project management documents.
- What was tested: the documents against the subject's list of examples.
- What is next: README, packaging, and the final test pass. [Add the actual work from this session.]