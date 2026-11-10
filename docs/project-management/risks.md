# Risks

- **Maze package interface changes at peer review.** Mitigation: the adapter isolates the package, so only one file changes.
- **Ghost difficulty.** Mitigation: ghost speed and grace period are single values that can be tuned.
- **Integration mismatch with the frontend.** Mitigation: a single shared types file and a snapshot-only read.
- **Config values change at the defense.** Mitigation: config is table-driven, and unknown keys are ignored.
- **Packaged build paths.** Mitigation: test the packaged game on a machine without the source tree.
- **Display and keyboard differences:** automated checks use SDL dummy video; finish interactive resizing, focus and text-entry checks on each target display/OS.
- **Distribution trust:** the local macOS app is not Developer ID signed/notarized. Public distribution needs release credentials; Windows/Linux builds must be made on those platforms.
- **Assignment MLX-equivalence:** the existing subject check remains open. Review drawing, fonts, events, timing and scaling APIs before submission; packaging success does not establish subject compliance.
