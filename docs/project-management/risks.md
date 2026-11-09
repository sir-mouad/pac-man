# Risks

- **Maze package interface changes at peer review.** Mitigation: the adapter isolates the package, so only one file changes.
- **Ghost difficulty.** Mitigation: ghost speed and grace period are single values that can be tuned.
- **Integration mismatch with the frontend.** Mitigation: a single shared types file and a snapshot-only read.
- **Config values change at the defense.** Mitigation: config is table-driven, and unknown keys are ignored.
- **Packaged build paths.** Mitigation: test the packaged game on a machine without the source tree.
- **Frontend risks:** to be filled in by the teammate.