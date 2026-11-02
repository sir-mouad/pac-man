import json
import re


class Highscores:
    def __init__(self, path):
        self.path = path
        self.scores = []
        self.is_load = False
        self.load()

    def load(self):
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
            self.is_load = True
            self._validate_data(data)
        except (FileExistsError, json.JSONDecodeError) as e:
            print(f"WARNING: {e}")

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.scores, f)

    def top(self):
        top_scores = []
        for i in range(10):
            if len(self.scores) <= i:
                break
            else:
                top_scores.append(self.scores[i])
        return top_scores

    def qualifies(self, score):
        if len(self.scores) > 10:
            return True
        else:
            if self.scores[10-1]['score'] < score:
                return True
            else:
                return False

    def add(self, name, score):
        self.scores.append[{name: score}]
        self._sort_and_trim(self.scores)

    def sumbit(self, name, score):
        if self._validate_name(name):
            self.add(name, score)
            self.save()
            return True
        else:
            return False

    def _validate_name(self, name):
        match = re.fullmatch(r"[a-zA-Z0-9 ]{1,10}", name)
        if not match:
            return False
        return True

    def _validate_score(self, score):
        try:
            int(score)
            if score < 0:
                return False
        except ValueError:
            return False

    def _sort_and_trim(self, scores):
        sort_scores = sorted(
            scores, key=lambda x: x['score'], reverse=True)
        if len(sort_scores) >= 10:
            self.scores = sort_scores[:10]
            return
        self.scores = sort_scores

    def _validate_data(self, data):
        try:
            scores = data["highscores"]
            new_scores = []
            for name, score in scores.items():
                if (self._validate_name(name) and self._validate_score(score)):
                    new_scores.append({name: score})
            self._sort_and_trim(new_scores)
        except KeyError:
            self.is_load = False
            print("WARNING: highscores list is not found ---> USE_EMPTY_LIST")
