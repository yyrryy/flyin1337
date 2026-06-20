MAP?=map.txt

run:
	uv run python3 main.py $(MAP)

install:
	uv sync

debug:
	uv run python3 -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

lint:
	flake8 *.py --max-line-length=88 --extend-ignore=E203
	mypy *.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


.PHONY: install run debug clean lint lint-strict