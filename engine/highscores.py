import json
from contextlib import suppress
import os
from pathlib import Path
import re
import tempfile


MAX_SCORES = 10
MAX_NAME_LENGTH = 10


class Highscores:
    def __init__(self, path):
        self.path = Path(path)
        self.scores = []
        self.last_error = ""
        self.is_load = False
        self.load()

    def load(self):
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

    def save(self):
        temporary = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=self.path.parent,
                    prefix=".highscores-", suffix=".tmp", delete=False) as f:
                temporary = Path(f.name)
                json.dump({"highscores": self.scores}, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, self.path)
        except OSError as e:
            print(f"WARNING: cannot save highscores ({e})")
            self.last_error = "Couldn't save your score. Check folder permissions."
            return False
        finally:
            if temporary is not None:
                with suppress(OSError):
                    temporary.unlink(missing_ok=True)
        self.last_error = ""
        return True

    def top(self, n=MAX_SCORES):
        return [dict(entry) for entry in self.scores[:n]]

    def qualifies(self, score):
        if len(self.scores) < MAX_SCORES:
            return True
        return score > self.scores[-1]["score"]

    def add(self, name, score):
        self.scores.append({"name": name, "score": score})
        self._sort_and_trim(self.scores)

    def submit(self, name, score):
        self.last_error = ""
        clean_name = self._validate_name(name)
        if clean_name is None:
            self.last_error = "Use 1-10 letters, numbers or spaces."
            return False
        previous = list(self.scores)
        self.add(clean_name, score)
        if not self.save():
            self.scores = previous
            return False
        return True

    def _validate_name(self, name):
        if not isinstance(name, str):
            return None
        cleaned = name.strip()
        if re.fullmatch(r"[a-zA-Z0-9 ]{1,10}", cleaned):
            return cleaned
        return None

    def _validate_score(self, score):
        if isinstance(score, bool):
            return None
        try:
            value = int(score)
        except (TypeError, ValueError):
            return None
        if value < 0:
            return None
        return value

    def _sort_and_trim(self, scores):
        self.scores = sorted(
            scores, key=lambda x: x["score"], reverse=True)[:MAX_SCORES]

    def _validate_data(self, data):
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
        valid = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = self._validate_name(entry.get("name"))
            score = self._validate_score(entry.get("score"))
            if name is not None and score is not None:
                valid.append({"name": name, "score": score})
        self._sort_and_trim(valid)
        self.is_load = True
