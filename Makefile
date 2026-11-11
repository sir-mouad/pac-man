ARG=config.json


install:
	uv sync

run:
	uv run python pac-man.py $(ARG)

debug:
	uv run python -m pdb pac-man.py $(ARG)

test:
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python -m unittest discover -s tests -v

build:
	uv run --group build python scripts/build.py

check-build:
	uv run python scripts/check_build.py

clean:
	find . -type d -name "__pycache__" -not -path './.venv/*' -exec rm -rf {} +
	rm -rf .mypy_cache build

lint:
	uv run flake8 frontend tests scripts pac-man.py --max-line-length=88
	uv run mypy frontend --follow-imports=silent --ignore-missing-imports
