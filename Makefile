run:
	python3 main.py map.txt

install:
	pip install -r requirements.txt

debug:
	python3 -m pdb main.py maps.txt

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

lint:
	flake8 . --max-line-length=88 --extend-ignore=E203
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . --max-line-length=88 --extend-ignore=E203
	mypy . --strict

.PHONY: install run debug clean lint lint-strict