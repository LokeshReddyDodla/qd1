.PHONY: help setup start stop clean test ingest query logs frontend

help:
	@echo "Patient Data RAG System - Available Commands:"
	@echo ""
	@echo "  make setup         - Install dependencies and create .env from template"
	@echo "  make start         - Start all services (Qdrant, Postgres, MongoDB)"
	@echo "  make stop          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - View service logs"
	@echo "  make run           - Run FastAPI application"
	@echo "  make frontend      - Open frontend in browser"
	@echo "  make setup-db      - Populate sample data into databases"
	@echo "  make test-ingest   - Run ingestion tests"
	@echo "  make test-query    - Run query tests"
	@echo "  make test          - Run all tests"
	@echo "  make clean         - Remove containers and volumes"
	@echo "  make clean-all     - Remove everything including Qdrant data"
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
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "✓ Services started"
	@echo "  Qdrant: http://localhost:6333"
	@echo "  Postgres: localhost:5432"
	@echo "  MongoDB: localhost:27017"

stop:
	@echo "Stopping services..."
	docker-compose stop

restart:
	@echo "Restarting services..."
	docker-compose restart

logs:
	docker-compose logs -f

run:
	@echo "Starting FastAPI application..."
	python main.py

setup-db:
	@echo "Setting up sample data in databases..."
	python setup_db.py

test-ingest:
	@echo "Running ingestion tests..."
	python test_ingestion.py

test-query:
	@echo "Running query tests..."
	python test_query.py

test: test-ingest test-query
	@echo "All tests completed"

clean:
	@echo "Stopping and removing containers..."
	docker-compose down
	@echo "✓ Cleaned up"

clean-all:
	@echo "Removing everything including data volumes..."
	docker-compose down -v
	rm -rf qdrant_storage/
	@echo "✓ Deep clean completed"

status:
	@echo "Service status:"
	@docker-compose ps

collection-info:
	@curl -s http://localhost:8000/collection/info | python -m json.tool

frontend:
	@echo "Opening frontend in browser..."
	@open http://localhost:8000 || xdg-open http://localhost:8000 || start http://localhost:8000
	@echo "If browser didn't open, navigate to: http://localhost:8000"

