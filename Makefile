.PHONY: build
ARG=config.json

install:
	uv sync
	@unzip -o mazegenerator-00001.zip -d /tmp/mazegen
	@if [ ! -d mazegenerator ]; then \
		unzip -o /tmp/mazegen/*.whl -d /tmp/mazegen/wheel; \
		cp -r /tmp/mazegen/wheel/mazegenerator .; \
		echo "mazegenerator installed"; \
	else \
		echo "mazegenerator already exists"; \
	fi

run:
	uv run python pac-man.py $(ARG)

debug:
	uv run python -m pdb pac-man.py $(ARG)

build:
	pyinstaller --onefile --name pac-man --add-data "config.json:." pac-man.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	flake8 . --exclude .venv,mazegenerator
	mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs --exclude ./mazegenerator