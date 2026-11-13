import json
import re
from pathlib import Path
from typing import Any


class Highscores:
    """Top-10 highscore list saved as JSON on disk."""
    last_error: str | None  # never set; reading it raises AttributeError

    def __init__(self, path: Any) -> None:
        """Load the highscore file at path when the object is created."""
        self.path = path
        self.scores: list[dict[str, Any]] = []
        self.is_load = False
        self.load()

    def load(self) -> None:
        """Read scores from the JSON file, or start with an empty list."""
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.scores = []
            self.is_load = False
            return
        except (OSError, json.JSONDecodeError) as e:
            print(f"WARNING: cannot read highscores ({e}) ---> USE_EMPTY_LIST")
            self.scores = []
            self.is_load = False
            return
        self._validate_data(data)

    def save(self) -> None:
        """Write scores to disk, printing a warning instead of crashing."""
        try:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w") as f:
                json.dump({"highscores": self.scores}, f, indent=4)
        except PermissionError as e:
            print("WARNING: Whoever set the permissions to 000, "
                  f"what were you thinking? 😑😑😑  ({e}")
        except OSError as e:
            print(f"WARNING: cannot save highscores ({e})")

    def top(self, n: int = 10) -> list[dict[str, Any]]:
        """Return the first n highscore entries."""
        return [dict(entry) for entry in self.scores[:n]]

    def qualifies(self, score: int) -> bool:
        """Return True if score would enter the top 10."""
        if len(self.scores) < 10:
            return True
        return score > self.scores[-1]["score"]  # type: ignore[no-any-return]

    def add(self, name: str, score: int) -> None:
        """Add a new entry and keep only the top 10."""
        self.scores.append({"name": name, "score": score})
        self._sort_and_trim(self.scores)

    def submit(self, name: str, score: int) -> bool:
        """Validate the name, save the score, and return True on success."""
        clean_name = self._validate_name(name)
        if clean_name is None:
            return False
        self.add(clean_name, score)
        self.save()
        return True

    def _validate_name(self, name: Any) -> str | None:
        """Return the trimmed name if it has 1-10 letters, digits or spaces."""
        if not isinstance(name, str):
            return None
        cleaned = name.strip()
        if re.fullmatch(r"[a-zA-Z0-9 ]{1,10}", cleaned):
            return cleaned
        return None

    def _validate_score(self, score: Any) -> int | None:
        """Return the score as a non-negative integer, or None if invalid."""
        if isinstance(score, bool):
            return None
        try:
            value = int(score)
        except (TypeError, ValueError):
            return None
        if value < 0:
            return None
        return value

    def _sort_and_trim(self, scores: list[dict[str, Any]]) -> None:
        """Sort entries from highest to lowest and keep the top 10."""
        self.scores = sorted(
            scores, key=lambda x: x["score"], reverse=True)[:10]

    def _validate_data(self, data: Any) -> None:
        """Keep only the valid entries from the loaded data."""
        try:
            entries = data["highscores"]
        except (KeyError, TypeError):
            print("WARNING: highscores list is not found ---> USE_EMPTY_LIST")
            self.scores = []
            self.is_load = False
            return
        if not isinstance(entries, list):
            print("WARNING: highscores is not a list ---> USE_EMPTY_LIST")
            self.scores = []
            self.is_load = False
            return
        valid: list[dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = self._validate_name(entry.get("name"))
            score = self._validate_score(entry.get("score"))
            if name is not None and score is not None:
                valid.append({"name": name, "score": score})
        self._sort_and_trim(valid)
        self.is_load = True
