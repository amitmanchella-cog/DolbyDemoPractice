.PHONY: install run lint test

install:
	python -m pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --port 8000

lint:
	ruff check .
	ruff format --check .

test:
	pytest -v
