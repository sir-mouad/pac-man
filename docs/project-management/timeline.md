# Timeline

Project period: 15-10-2026 to 14-11-2026

## Planned phases
1. Config parser and maze adapter
2. Movement and game rules
3. Highscore store
4. Ghost AI and engine
5. Gameplay fixes and cheat mode
6. Frontend integration (sreja)
7. Packaging, README, and documents

## What actually happened
- Phases 1 and 2 took longer than planned. The maze package interface and the direction and wall logic needed more debugging than expected.
- The ghost AI was designed around fixed targeting behaviors for each ghost, rather than the random movement first considered. Random movement was dropped, and each ghost follows its own target rule.
- The highscore store was written and reviewed after the engine was started, so the order changed.
- Gameplay fixes (timing, respawn, edible expiry, grace period, level advance) came after integration testing, not before.
- Frontend integration was implemented on 2026-11-10: all screens, input, snapshot rendering and score entry are wired to the engine. Automated integration checks and rendered UI inspection cover the frontend; interactive target-display checks remain.
- Packaging and the documents are at the end, as planned.
