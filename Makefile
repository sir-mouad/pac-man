install:
	uv sync

run:
	uv run python -m pac-man $(arg)

debug:
	uv run python -m pdb pac-man $(arg)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs