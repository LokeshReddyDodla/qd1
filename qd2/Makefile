.PHONY: help setup start stop clean test ingest query logs frontend docker-build docker-up docker-down docker-logs docker-restart

help:
	@echo "Patient Data RAG System - Available Commands:"
	@echo ""
	@echo "Local Development:"
	@echo "  make setup         - Install dependencies and create .env from template"
	@echo "  make start         - Start all services (Qdrant, Postgres, MongoDB)"
	@echo "  make stop          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - View service logs"
	@echo "  make run           - Run FastAPI application"
	@echo "  make frontend      - Open frontend in browser"
	@echo "  make test          - Run all tests"
	@echo "  make clean         - Remove containers and volumes"
	@echo ""
	@echo "Docker Deployment:"
	@echo "  make docker-build  - Build Docker image for app"
	@echo "  make docker-up     - Start all services in Docker (including app)"
	@echo "  make docker-down   - Stop all Docker services"
	@echo "  make docker-restart- Restart Docker services"
	@echo "  make docker-logs   - View Docker logs (all services)"
	@echo "  make docker-logs-app - View app logs only"
	@echo "  make docker-rebuild- Rebuild and restart app container"
	@echo "  make docker-clean  - Remove all containers and volumes (⚠️  deletes data)"
	@echo "  make docker-shell  - Open shell in app container"
	@echo "  make docker-status - Show status of all containers"
	@echo ""

setup:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp env_template.txt .env; \
		echo "⚠️  Please edit .env and add your OPENAI_API_KEY"; \
	else \
		echo ".env already exists"; \
	fi

start:
	@echo "Starting services..."
	docker-compose up -d qdrant postgres mongodb
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "✓ Services started"
	@echo "  Qdrant: http://localhost:6333"
	@echo "  Postgres: localhost:5432"
	@echo "  MongoDB: localhost:27017"

stop:
	@echo "Stopping services..."
	docker-compose stop qdrant postgres mongodb

restart:
	@echo "Restarting services..."
	docker-compose restart qdrant postgres mongodb

logs:
	docker-compose logs -f qdrant postgres mongodb

run:
	@echo "Starting FastAPI application..."
	python main.py

test:
	@echo "Running tests..."
	pytest -v

clean:
	@echo "Stopping and removing containers..."
	docker-compose down qdrant postgres mongodb
	@echo "✓ Cleaned up"

clean-all:
	@echo "Removing everything including data volumes..."
	docker-compose down -v
	rm -rf qdrant_storage/
	@echo "✓ Deep clean completed"

status:
	@echo "Service status:"
	@docker-compose ps

# Docker Deployment Commands
docker-build:
	@echo "Building Docker image..."
	docker-compose build app

docker-up:
	@echo "Starting all services in Docker (including app)..."
	docker-compose up -d
	@echo ""
	@echo "✓ All services started!"
	@echo "  Application: http://localhost:1531"
	@echo "  API Docs: http://localhost:1531/docs"
	@echo "  Qdrant: http://localhost:6333"
	@echo ""
	@echo "Check status: make docker-status"
	@echo "View logs: make docker-logs"

docker-down:
	@echo "Stopping all Docker services..."
	docker-compose down

docker-restart:
	@echo "Restarting all Docker services..."
	docker-compose restart

docker-logs:
	@echo "Viewing logs (Ctrl+C to exit)..."
	docker-compose logs -f

docker-logs-app:
	@echo "Viewing app logs (Ctrl+C to exit)..."
	docker-compose logs -f app

docker-rebuild:
	@echo "Rebuilding and restarting app..."
	docker-compose build app
	docker-compose up -d app
	@echo "✓ App rebuilt and restarted"

docker-clean:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "✓ All containers and volumes removed"; \
	else \
		echo "Cancelled"; \
	fi

docker-shell:
	@echo "Opening shell in app container..."
	docker-compose exec app bash

docker-status:
	@echo "Docker container status:"
	@echo ""
	@docker-compose ps
	@echo ""
	@echo "Health checks:"
	@docker inspect qd2-app qd2-qdrant qd2-postgres qd2-mongodb 2>/dev/null | \
		jq -r '.[] | "\(.Name): \(.State.Health.Status // "N/A")"' 2>/dev/null || \
		echo "Install jq for detailed health status: brew install jq"

frontend:
	@echo "Opening frontend in browser..."
	open http://localhost:1531 || xdg-open http://localhost:1531 || echo "Please open http://localhost:1531 in your browser"


collection-info:
	@curl -s http://localhost:8000/collection/info | python -m json.tool

frontend:
	@echo "Opening frontend in browser..."
	@open http://localhost:8000 || xdg-open http://localhost:8000 || start http://localhost:8000
	@echo "If browser didn't open, navigate to: http://localhost:8000"

