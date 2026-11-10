"""Copy the distribution away from the repo, then run it without Python."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    app_bundle = sys.platform == "darwin"
    name = "Pac-Man.app" if app_bundle else "Pac-Man"
    source = root / "dist" / name
    if not source.exists():
        raise SystemExit("Run make build first.")
    with tempfile.TemporaryDirectory(prefix="pac-man-release-") as directory:
        temp = Path(directory).resolve()
        copied = temp / name
        shutil.copytree(source, copied, symlinks=True)
        if app_bundle:
            executable = copied / "Contents/MacOS/Pac-Man"
        else:
            executable = copied / ("Pac-Man.exe" if os.name == "nt" else "Pac-Man")
        env = dict(os.environ, PACMAN_DATA_DIR=str(temp / "data"))
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        for args in ([], [str(temp / "custom.json")]):
            if args:
                config = (root / "config.json").read_text()
                (temp / "custom.json").write_text(config)
            result = subprocess.run(
                [str(executable), *args, "--smoke-test"], cwd=temp,
                env=env, capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise SystemExit(result.stdout + result.stderr)
            if "20x15; 4 ghosts" not in result.stdout:
                raise SystemExit(f"Unexpected smoke result: {result.stdout}")
            if str(root) in result.stdout:
                raise SystemExit("Bundle still references the source directory.")
            expected_scores = (temp / "highscores.json" if args
                               else temp / "data/highscores.json")
            if str(expected_scores) not in result.stdout:
                raise SystemExit("Incorrect highscore path.")
            print(result.stdout.strip())
        print(json.dumps({"standalone": "PASS", "copied_bundle": name,
                          "source_required": False}))


if __name__ == "__main__":
    main()
