# Timeline

Project period: 15-10-2026 to 14-11-2026. Work continued on 15-11-2026 for the demo build and the cheat mode.

## Planned phases
1. Config parser and maze adapter
2. Movement and game rules
3. Highscore store
4. Ghost AI and engine
5. Gameplay fixes and cheat mode
6. Frontend integration
7. Packaging, README, and documents

## What actually happened
- Phases 1 and 2 took longer than planned. The maze package interface and the direction and wall logic needed more debugging than expected.
- The ghost AI uses fixed targeting rules for each ghost, not the random movement first considered.
- The highscore store was reviewed after the engine had started, so the order changed.
- Gameplay fixes (timing, respawn, edible expiry, level advance) came after integration testing, not before.
- The frontend was integrated on 10-11-2026: all screens, input, snapshot rendering and score entry are wired to the engine.
- 13-11-2026: lint and type fixes, the README, and the first standalone build for the demo.
- 14-11-2026: cleanup. The launcher now uses the engine's config parser, the unused frontend path module was removed, invalid config data is handled, and the optional `imposible_levels` key was added.
- 15-11-2026: cheat keys shown on the play screen and in a guide page from How To Play.
- Packaging and documents were done at the end, as planned, and the Linux build was uploaded to Itch.io as an unlisted demo.
- Not done yet: interactive playtesting, the MLX equivalence review, and Windows and macOS builds. See requirements.md.
