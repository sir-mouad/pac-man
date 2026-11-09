from tester import run
import sys


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config_path>")
        sys.exit(1)
    run()
