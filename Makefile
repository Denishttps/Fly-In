PYTHON    := uv run python
SRC       := src
MAIN      := $(SRC)/__main__.py
MAP       ?= maps/easy/01_linear_path.txt

.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	$(PYTHON) $(MAIN) --path $(MAP)


debug:
	$(PYTHON) -m pdb $(MAIN) --path $(MAP)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc"     -delete
	find . -type f -name "*.pyo"     -delete
	rm -rf .mypy_cache

lint:
	$(PYTHON) -m flake8 src
	$(PYTHON) -m mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 src
	$(PYTHON) -m mypy . --strict