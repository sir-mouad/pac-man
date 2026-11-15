# Risks

- **Maze package interface changes at the defense.** Mitigation: `engine/maze_adapter.py` isolates the package, so only that file changes.
- **Ghost difficulty.** Mitigation: ghost speeds, the respawn and protection times, and `imposible_levels` are single values that can be tuned.
- **Config values change at the defense.** Mitigation: the config is read through one table in `engine/parser.py`, and unknown keys are ignored.
- **Engine and frontend out of step.** Mitigation: shared types live in one file, and the frontend reads only the snapshot.
- **Packaged build on other systems.** Only the Linux build has been made and run. Windows and macOS builds must be made on their own systems.
- **Highscore file in an unexpected place.** The file is relative to the folder the game is started from. Mitigation: set an absolute `highscore_filename` in the config, or start the game from the project folder.
- **Level timer does not count real time.** It only counts while Pac-Man moves, so it may not be judged as a time limit. Mitigation: decide the rule before the defense and document it.
- **No automated tests in the repository.** Regressions are caught only by `make lint` and by hand. Mitigation: the manual checklist in test-plan.md.
- **Display and keyboard differences.** Checks so far used headless rendering. Mitigation: play on each target display and keyboard before the defense.
