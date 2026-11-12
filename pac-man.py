"""Source and standalone entry point for the Pac-Man arcade."""

import argparse
import os
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from engine.engine import GameEngine
from engine.parser import Parser
from frontend.paths import default_config, score_path


def main() -> None:
    parser = argparse.ArgumentParser(description="PAC-MAN / One more round")
    parser.add_argument("config", nargs="?", type=Path,
                        help="custom config; relative score paths use its folder")
    parser.add_argument("--smoke-test", action="store_true",
                        help="check the bundle without opening a window")
    args = parser.parse_args()
    if args.smoke_test:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"

    from frontend.app import Application
    import pygame

    config_path = args.config.resolve() if args.config else default_config()
    config = Parser().get_config(config_path)
    highscores = score_path(config["highscore_filename"], args.config)
    app = Application(GameEngine(config, highscores))
    if args.smoke_test:
        app.start()
        app.update(1 / 60)
        app.draw()
        app.present()
        print(f"OK: level {app.snapshot.level}; "
              f"{app.snapshot.width}x{app.snapshot.height}; "
              f"{len(app.snapshot.ghosts)} ghosts")
        print(f"Config: {config_path}\nHighscores: {highscores}")
        pygame.quit()
    else:
        app.run()


if __name__ == "__main__":
    main()
