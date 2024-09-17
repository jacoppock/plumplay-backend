# Makefile

# Define docker-compose as a variable for ease of use
DC := docker-compose

# Default target
.PHONY: help venv requirements init install-dev lint build up down restart logs migrate createsuperuser collectstatic shell test coverage environment api-docs check-api-docs

# Variables
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python
DJANGO_MANAGE := $(PYTHON_VENV) src/manage.py

# Default target
help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

venv: ## Create a virtual environment
	@$(PYTHON) -m venv $(VENV)
	@$(PIP) install -U pip pip-tools

requirements: venv ## Compile requirements files
	@$(PIP) install pip-tools
	@$(VENV)/bin/pip-compile -v --output-file requirements/requirements.txt pyproject.toml
	@$(VENV)/bin/pip-compile -v --extra dev --output-file requirements/requirements-dev.txt pyproject.toml

init: venv requirements ## Initialize the project
	@$(PIP) install -r requirements/requirements-dev.txt

install-dev: venv ## Install development dependencies
	@$(PIP) install -r requirements/requirements-dev.txt

lint: ## Run linters
	@$(VENV)/bin/ruff check src tests
	@$(VENV)/bin/black src tests
	@$(VENV)/bin/isort src tests
	@$(VENV)/bin/mypy src tests


down: ## Stop Docker containers
	$(DC) down

start:
	docker compose --env-file=.env up --build -d

restart: down up ## Restart Docker containers

logs: ## View Docker container logs
	$(DC) logs -f

migrate: ## Apply database migrations
	$(DC) exec web $(DJANGO_MANAGE) migrate

createsuperuser: ## Create a Django superuser
	$(DC) exec web $(DJANGO_MANAGE) createsuperuser

collectstatic: ## Collect static files
	$(DC) exec web $(DJANGO_MANAGE) collectstatic --noinput

shell: ## Open Django shell
	$(DC) exec web $(DJANGO_MANAGE) shell

test: ## Run tests
	@$(VENV)/bin/pytest tests

coverage: ## Run tests with coverage
	@$(VENV)/bin/pytest --cov=src tests
	@$(VENV)/bin/coverage html
	@echo "Coverage report generated. Open htmlcov/index.html in your browser."

environment: .env ## Create .env file if it doesn't exist
.env:
	@cp .env.example .env
	@echo "Created .env file. Please update it with your settings."

api-docs: ## Generate API documentation
	@$(DJANGO_MANAGE) export_openapi_schema --api base.urls.api_v1 --output docs/openapi.json
	@echo "OpenAPI schema exported to docs/openapi.json"

check-api-docs: ## Check if API docs are up to date
	@$(DJANGO_MANAGE) export_openapi_schema --api base.urls.api_v1 --output docs/openapi_new.json
	@diff docs/openapi.json docs/openapi_new.json || (echo "API docs are out of date. Run 'make api-docs' to update." && exit 1)
	@rm docs/openapi_new.json