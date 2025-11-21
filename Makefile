.PHONY: help build up down logs clean install-frontend install-backend test migrate

help:
	@echo "MemoryGuard Development Commands"
	@echo "================================="
	@echo "make build              - Build all Docker containers"
	@echo "make up                 - Start all services"
	@echo "make down               - Stop all services"
	@echo "make logs               - View logs from all services"
	@echo "make migrate            - Run database migrations"
	@echo "make clean              - Remove all containers and volumes"
	@echo "make install-frontend   - Install frontend dependencies"
	@echo "make install-backend    - Install backend dependencies"
	@echo "make test               - Run all tests"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf frontend/node_modules
	rm -rf backend/venv

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt

migrate:
	docker-compose exec backend alembic upgrade head

test:
	cd frontend && npm test
	cd backend && pytest
