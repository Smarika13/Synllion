.PHONY: help build up down logs shell db migrate test

help:
	@echo "Synllion Backend Commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - Show all logs"
	@echo "  make logs-back  - Show backend logs"
	@echo "  make shell-back - Open shell in backend container"
	@echo "  make shell-db   - Open PostgreSQL shell"
	@echo "  make migrate    - Run database migrations"
	@echo "  make test       - Run tests"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-back:
	docker-compose logs -f backend

shell-back:
	docker-compose exec backend bash

shell-db:
	docker-compose exec postgres psql -U synllion_user -d synllion

migrate:
	docker-compose exec backend alembic upgrade head

test:
	docker-compose exec backend pytest