# Makefile for Bot Management Dashboard

.PHONY: help dev build up down logs clean install test format lint

# Default target
help:
	@echo "Bot Management Dashboard - Available commands:"
	@echo ""
	@echo "  make dev         - Start development environment"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make format      - Format code"
	@echo "  make lint        - Lint code"

# Development
dev:
	docker-compose up

# Build images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean up
clean:
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf frontend/.next
	rm -rf frontend/node_modules
	rm -rf backend/venv

# Install dependencies
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cd bots/examples && pip install -r requirements.txt

# Run tests
test:
	cd backend && pytest
	cd frontend && npm run test

# Format code
format:
	cd backend && black app/
	cd frontend && npm run format

# Lint code
lint:
	cd backend && flake8 app/
	cd frontend && npm run lint

# Database
db-init:
	cd backend && python -c "from app.database import init_db; init_db()"

# Production
prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f
