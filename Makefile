.PHONY: help doctor start-1060 start-1080 start-turbo status stop chat smoke bench clean install

.DEFAULT_GOAL := help

help: ## Show this help
	@echo "Kimari Local AI — Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install Python dependencies
	pip install -r cli/requirements.txt

doctor: ## Run system diagnostics
	cd cli && python kimari_cli.py doctor

start-1060: ## Start Kimari with GTX 1060 profile
	cd cli && python kimari_cli.py start --profile gtx1060

start-1080: ## Start Kimari with GTX 1080 profile
	cd cli && python kimari_cli.py start --profile gtx1080

start-turbo: ## Start Kimari with Turbo profile
	cd cli && python kimari_cli.py start --profile turbo

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

clean: ## Clean build artifacts
	@echo "Cleaning..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info .pytest_cache
	@echo "Done."
