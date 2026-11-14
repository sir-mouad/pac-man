"""Source and standalone entry point for the Pac-Man arcade."""

import sys
from engine.engine import GameEngine
from engine.parser import Parser
from frontend.app import Application


def main() -> None:
    """load the config, and start the game."""

    config = Parser().get_config()
    app = Application(GameEngine(config))
    app.run()


if __name__ == "__main__":
    try:
        if len(sys.argv) > 2:
            raise ValueError("Usage : use python3 pac-man.py <config_path>")
        main()
    except KeyboardInterrupt:
        print("\nGame interrupted by user. Exiting...")
    except Exception as e:
        print(e)
