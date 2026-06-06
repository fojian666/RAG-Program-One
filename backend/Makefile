.PHONY: dev test lint format migrate up down

# Install dependencies
install:
	pip install -e ".[dev,ml]"

# Run FastAPI dev server
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest -v

# Lint & format
lint:
	ruff check src tests main.py

format:
	ruff format src tests main.py

# Database migrations
migrate:
	alembic upgrade head

migrate-make:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

# Docker compose
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
