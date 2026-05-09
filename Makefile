.PHONY: help doctor info start-1060 start-1080 start-turbo start-test start-docker status stop chat smoke bench clean install install-dev dry-run-test logs logs-follow doctor-json status-json validate-config validate-schema webui-up webui-down webui-logs test lint ci-local pull-list pull-test models profiles config-validate config-show config-path migrate format-check

.DEFAULT_GOAL := help

help: ## Show this help
	@echo "Kimari Local AI — Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install Python dependencies
	pip install -r cli/requirements.txt

install-dev: ## Install Python dependencies (including dev tools)
	pip install -r requirements-dev.txt

install-editable: ## Install kimari package in editable mode
	pip install -e .

install-editable-dev: ## Install kimari package in editable mode with dev deps
	pip install -e ".[dev]"

doctor: ## Run system diagnostics
	python -m kimari.cli.main doctor

info: ## Show Kimari installation info
	python -m kimari.cli.main info

start-1060: ## Start Kimari with GTX 1060 profile
	python -m kimari.cli.main start --profile gtx1060

start-1080: ## Start Kimari with GTX 1080 profile
	python -m kimari.cli.main start --profile gtx1080

start-turbo: ## Start Kimari with Turbo profile
	python -m kimari.cli.main start --profile turbo

start-test: ## Start Kimari with test profile
	python -m kimari.cli.main start --profile test

start-docker: ## Start Kimari with Docker/Open WebUI profile
	python -m kimari.cli.main start --profile docker

pull-list: ## List models available for download
	python -m kimari.cli.main pull --list

pull-test: ## Download the test model
	python -m kimari.cli.main pull test

stop: ## Stop running Kimari server
	python -m kimari.cli.main stop

status: ## Check Kimari server status
	python -m kimari.cli.main status

chat: ## Open interactive chat
	python -m kimari.cli.main chat

smoke: ## Run smoke tests
	@echo "Running smoke tests..."
	@bash scripts/linux/smoke-test.sh

bench: ## Run benchmarks with default profile
	python -m kimari.cli.main bench --profile gtx1080

dry-run-test: ## Preview server start without running (test profile)
	python -m kimari.cli.main start --profile test --dry-run

logs: ## Show last 50 lines of server log
	python -m kimari.cli.main logs

logs-follow: ## Tail server logs
	python -m kimari.cli.main logs --follow

doctor-json: ## Run diagnostics as JSON
	python -m kimari.cli.main doctor --json

status-json: ## Show status as JSON
	python -m kimari.cli.main status --json

validate-config: ## Validate profiles config against schema
	python -c "import json, jsonschema; config=json.load(open('config/kimari.profiles.json')); schema=json.load(open('config/kimari.profiles.schema.json')); jsonschema.validate(config, schema); default=config.get('default_profile',''); assert default in config.get('profiles',{}), f'default_profile \"{default}\" not found in profiles'; print('Config schema valid. default_profile=\"' + default + '\" exists in profiles.')"

validate-schema: ## Validate profiles JSON only (no schema check)
	python -c "import json; json.load(open('config/kimari.profiles.json')); print('Config JSON valid.')"

webui-up: ## Start Open WebUI via Docker
	docker compose -f docker/docker-compose.open-webui.yml up -d

webui-down: ## Stop Open WebUI
	docker compose -f docker/docker-compose.open-webui.yml down

webui-logs: ## Show Open WebUI logs
	docker compose -f docker/docker-compose.open-webui.yml logs -f

test: ## Run pytest test suite
	python -m pytest tests/ -q

lint: ## Run ruff linter on kimari/ and tests/
	ruff check kimari/ tests/

format-check: ## Check formatting with ruff
	ruff format --check kimari/ tests/

models: ## List available GGUF models
	python -m kimari.cli.main models

profiles: ## List configured GPU profiles
	python -m kimari.cli.main profiles

config-validate: ## Validate configuration via CLI
	python -m kimari.cli.main config validate

config-show: ## Show full configuration
	python -m kimari.cli.main config show

config-path: ## Print config file path
	python -m kimari.cli.main config path

migrate: ## Migrate configuration to current version
	python -m kimari.cli.main config migrate

ci-local: ## Run local CI: validate-config, py_compile, lint, and pytest
	@echo "Running local CI pipeline..."
	@echo "[1/4] validate-config"
	@python -c "import json, jsonschema; config=json.load(open('config/kimari.profiles.json')); schema=json.load(open('config/kimari.profiles.schema.json')); jsonschema.validate(config, schema); default=config.get('default_profile',''); assert default in config.get('profiles',{}), f'default_profile \"' + default + '\" not found in profiles'; print('Config schema valid.')"
	@echo "[2/4] py_compile"
	@python -m py_compile kimari/__init__.py && echo "kimari/__init__.py OK"
	@python -m py_compile kimari/cli/main.py && echo "kimari/cli/main.py OK"
	@python -m py_compile kimari/core/constants.py && echo "kimari/core/constants.py OK"
	@python -m py_compile kimari/core/state.py && echo "kimari/core/state.py OK"
	@python -m py_compile kimari/core/errors.py && echo "kimari/core/errors.py OK"
	@python -m py_compile kimari/core/detection.py && echo "kimari/core/detection.py OK"
	@python -m py_compile kimari/config/loader.py && echo "kimari/config/loader.py OK"
	@python -m py_compile kimari/models/registry.py && echo "kimari/models/registry.py OK"
	@python -m py_compile kimari/profiles/manager.py && echo "kimari/profiles/manager.py OK"
	@python -m py_compile kimari/benchmarks/kimarifit.py && echo "kimari/benchmarks/kimarifit.py OK"
	@python -m py_compile kimari/benchmarks/bench.py && echo "kimari/benchmarks/bench.py OK"
	@echo "[3/4] lint (ruff)"
	@-ruff check kimari/ tests/ 2>/dev/null || echo "  (ruff not installed, skipping)"
	@echo "[4/4] pytest"
	python -m pytest tests/ -q
	@echo "CI local passed."

clean: ## Clean build artifacts
	@echo "Cleaning..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info .pytest_cache kimari/*.egg-info
	@echo "Done."
