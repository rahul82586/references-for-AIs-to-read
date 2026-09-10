# Makefile for Broker Platform

.PHONY: help install dev-install run test lint type-check clean migrate seed docker-up docker-down

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev-install: ## Install development dependencies
	pip install -e ".[dev]"

run: ## Start the API server
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests only
	pytest tests/e2e/ -v

test-coverage: ## Run tests with coverage report
	pytest tests/ --cov=broker-platform --cov-report=html --cov-report=term-missing

lint: ## Run linters (black, ruff)
	black . --check
	ruff check .

format: ## Format code with black
	black .
	ruff check . --fix

type-check: ## Run type checking with mypy
	mypy .

clean: ## Clean up build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ htmlcov/ .coverage
	rm -rf .venv/ venv/

migrate: ## Run database migrations
	alembic upgrade head

migrate-down: ## Rollback last migration
	alembic downgrade -1

migrate-create: ## Create new migration (usage: make migrate-create MSG="add users table")
	alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed database with initial data
	python -m cli.main seed

docker-up: ## Start Docker containers (PostgreSQL, Redis, etc.)
	docker-compose -f ops/docker/docker-compose.dev.yml up -d

docker-down: ## Stop Docker containers
	docker-compose -f ops/docker/docker-compose.dev.yml down

docker-logs: ## Show Docker container logs
	docker-compose -f ops/docker/docker-compose.dev.yml logs -f

cli: ## Run CLI command (usage: make cli CMD="status")
	python -m cli.main $(CMD)

backtest: ## Run backtest (usage: make backtest STRATEGY=my_strategy START=2024-01-01 END=2024-01-31)
	python -m cli.main backtest -s $(STRATEGY) --start $(START) --end $(END)

sync-node: ## Sync with cluster node (usage: make sync-node NODE_ID=node-2)
	python -m cli.main sync -n $(NODE_ID)

export-data: ## Export data (usage: make export-data TYPE=accounts OUTPUT=accounts.json)
	python -m cli.main export --type $(TYPE) --output $(OUTPUT)

import-data: ## Import data (usage: make import-data FILE=data.json)
	python -m cli.main import_data $(FILE)

docs: ## Generate documentation
	sphinx-quickstart docs || echo "Sphinx already initialized"
	sphinx-build -b html docs/ docs/_build/html

pre-commit: ## Run all pre-commit checks
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

setup-dev: ## Complete development setup
	$(MAKE) dev-install
	cp .env.example .env
	$(MAKE) docker-up
	$(MAKE) migrate
	$(MAKE) seed
	@echo "Development environment ready!"
