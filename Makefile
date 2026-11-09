ARG=config.json

install:
	uv sync

run:
	uv run python -m pac-man $(ARG)

debug:
	uv run python -m pdb pac-man $(ARG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	flake8 . --exclude .venv
	mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs