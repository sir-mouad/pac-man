ARG=config.json


install:
	uv sync

run:
	uv run python pac-man.py $(ARG)

debug:
	uv run python -m pdb pac-man.py $(ARG)

clean:
	find . -type d -name "__pycache__" -not -path './.venv/*' -exec rm -rf {} +
	rm -rf .mypy_cache build

lint:
	flake8 . --exclude .venv
	mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs --exclude .venv
