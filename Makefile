.PHONY: up down logs migrate test lint clean api-shell help

# Default compose file
COMPOSE := docker compose -f infra/docker-compose.yml

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

up: ## Build & start postgres, redis, api, worker (applies migrations)
	$(COMPOSE) up --build -d
	@echo "API:      http://localhost:8000/api/v1/health"
	@echo "Ready:    http://localhost:8000/api/v1/health/ready"
	@echo "Postgres: localhost:5432 (kisan/kisan)"
	@echo "Redis:    localhost:6379"

logs: ## Tail API logs
	$(COMPOSE) logs -f api

migrate: ## Run alembic migrations against the running db
	$(COMPOSE) run --rm migrate

test: ## Run backend tests inside the container
	$(COMPOSE) run --rm --no-deps api pytest -q

lint: ## Run ruff on backend
	$(COMPOSE) run --rm --no-deps api sh -c "ruff check app tests && ruff format --check app tests"

shell: ## Open a shell in the api container
	$(COMPOSE) exec api bash

down: ## Stop the stack (keeps volumes)
	$(COMPOSE) down

clean: ## Stop stack and delete volumes (destroys local data!)
	$(COMPOSE) down -v
