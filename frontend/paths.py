"""Paths that work from source, a frozen bundle, and any working directory."""

import os
from pathlib import Path
import sys


def resource_root() -> Path:
    """Return the folder that holds the game's bundled files."""
    return Path(__file__).resolve().parent.parent


def data_directory() -> Path:
    """Return the per-user folder for highscores and custom config."""
    override = os.environ.get("PACMAN_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Pac-Man"
    if sys.platform == "win32":
        root = Path(os.environ.get("APPDATA", str(Path.home())))
        return root / "Pac-Man"
    root = Path(os.environ.get("XDG_DATA_HOME",
                               str(Path.home() / ".local/share")))
    return root / "pac-man"


def default_config() -> Path:
    """Return the custom config if present, else the bundled one."""
    custom = data_directory() / "config.json"
    return custom if custom.is_file() else resource_root() / "config.json"


def score_path(filename: str, config_path: Path | None) -> Path:
    """Return the highscore path; relative names go beside the config."""
    path = Path(filename).expanduser()
    if path.is_absolute():
        return path
    if config_path is not None:
        return config_path.resolve().parent / path
    return data_directory() / path
