.PHONY: run dev test lint format check

# Variables
APP_MODULE = app.main:app
HOST = 0.0.0.0
PORT = 9000

# Start server
run:
	poetry run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)

# Start server with reload
dev:
	poetry run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

# Run tests
test:
	poetry run pytest

# Lint and format
lint:
	poetry run ruff check .
	poetry run mypy app

format:
	poetry run ruff format .

# Check types, format, and tests
check: format lint test
