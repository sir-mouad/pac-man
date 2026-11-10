"""Build from any directory; ship the resulting folder/app, never just its exe."""

import os
from pathlib import Path
import subprocess
import sys


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env.setdefault("PYINSTALLER_CONFIG_DIR", str(root / "build/pyinstaller"))
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
         "--distpath", str(root / "dist"), "--workpath", str(root / "build"),
         str(root / "Pac-Man.spec")], cwd=root, env=env, check=True)
    print(f"\nStandalone build ready in {root / 'dist'}")


if __name__ == "__main__":
    main()
