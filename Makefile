.PHONY: install seed run lint test

install:
	python -m pip install -r requirements-dev.txt

seed:
	python -m app.seed

run: seed
	uvicorn app.main:app --reload --port 8000

lint:
	ruff check .
	ruff format --check .

test:
	pytest -v
