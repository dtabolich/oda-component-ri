.PHONY: help start stop restart logs build clean test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

start: ## Start all services with docker-compose
	docker-compose up -d

stop: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Follow logs from all services
	docker-compose logs -f

logs-kratos: ## Follow Kratos logs
	docker-compose logs -f kratos

logs-sms: ## Follow SMS service logs (shows verification codes)
	docker-compose logs -f sms-service

logs-ui: ## Follow UI service logs
	docker-compose logs -f ui

build: ## Build all docker images
	docker-compose build

clean: ## Stop and remove all containers, volumes, and images
	docker-compose down -v --rmi all

test: ## Run tests
	@echo "Running tests..."
	cd ui && npm test
	cd backend && npm test

dev-kratos: ## Start only Kratos (for local dev)
	cd config && docker run --rm -it \
		-p 4433:4433 \
		-p 4434:4434 \
		-v $$(pwd):/etc/config/kratos \
		oryd/kratos:v1.0.4 \
		serve all --config /etc/config/kratos/kratos.yml

dev-sms: ## Start SMS service locally
	cd backend && npm install && npm start

dev-ui: ## Start UI service locally
	cd ui && npm install && npm start

install: ## Install all dependencies
	cd ui && npm install
	cd backend && npm install

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U kratos -d kratos

identity-list: ## List all identities
	curl -s http://localhost:4434/admin/identities | jq

health-check: ## Check health of all services
	@echo "Checking Kratos..."
	@curl -s http://localhost:4434/health/ready | jq
	@echo "\nChecking SMS Service..."
	@curl -s http://localhost:4436/health | jq
	@echo "\nChecking UI..."
	@curl -s http://localhost:3000/health | jq

open: ## Open UI in browser
	@echo "Opening http://localhost:3000"
	@which open > /dev/null && open http://localhost:3000 || which xdg-open > /dev/null && xdg-open http://localhost:3000 || echo "Please open http://localhost:3000 in your browser"
