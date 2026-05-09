.PHONY: help doctor start-1060 start-1080 start-turbo start-test status stop chat smoke bench clean install install-dev dry-run-test logs logs-follow doctor-json status-json validate-config validate-schema webui-up webui-down webui-logs

.DEFAULT_GOAL := help

help: ## Show this help
	@echo "Kimari Local AI — Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install Python dependencies
	pip install -r cli/requirements.txt

install-dev: ## Install Python dependencies (including dev tools)
	pip install -r requirements-dev.txt

doctor: ## Run system diagnostics
	cd cli && python kimari_cli.py doctor

start-1060: ## Start Kimari with GTX 1060 profile
	cd cli && python kimari_cli.py start --profile gtx1060

start-1080: ## Start Kimari with GTX 1080 profile
	cd cli && python kimari_cli.py start --profile gtx1080

start-turbo: ## Start Kimari with Turbo profile
	cd cli && python kimari_cli.py start --profile turbo

start-test: ## Start Kimari with test profile
	cd cli && python kimari_cli.py start --profile test

stop: ## Stop running Kimari server
	cd cli && python kimari_cli.py stop

status: ## Check Kimari server status
	cd cli && python kimari_cli.py status

chat: ## Open interactive chat
	cd cli && python kimari_cli.py chat

smoke: ## Run smoke tests
	@echo "Running smoke tests..."
	@bash scripts/linux/smoke-test.sh

bench: ## Run benchmarks with default profile
	cd cli && python kimari_cli.py bench --profile gtx1080

dry-run-test: ## Preview server start without running (test profile)
	cd cli && python kimari_cli.py start --profile test --dry-run

logs: ## Show last 50 lines of server log
	cd cli && python kimari_cli.py logs

logs-follow: ## Tail server logs
	cd cli && python kimari_cli.py logs --follow

doctor-json: ## Run diagnostics as JSON
	cd cli && python kimari_cli.py doctor --json

status-json: ## Show status as JSON
	cd cli && python kimari_cli.py status --json

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

clean: ## Clean build artifacts
	@echo "Cleaning..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info .pytest_cache
	@echo "Done."
