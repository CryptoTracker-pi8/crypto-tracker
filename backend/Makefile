VENV = .venv

# Default target
.DEFAULT_GOAL := help

install: ## Create venv and install dependencies with uv
	uv venv $(VENV)
	uv sync

run: ## Run app
	uv run uvicorn cryptotracker.__main__:app --host 0.0.0.0 --port 8080

dev: ## Run app with hot reload
	uv run uvicorn cryptotracker.__main__:app --reload --host 0.0.0.0 --port 8080

update: ## Update dependencies from pyproject.toml
	uv sync --upgrade

clean: ## Delete venv
	rm -rf $(VENV)

help: ## Show available make commands
	@echo "Available make targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
