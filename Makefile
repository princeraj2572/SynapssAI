.PHONY: dev install migrate seed test backup logs help

help:
	@echo "Personal Life OS - Available commands:"
	@echo "  make install   Install all dependencies"
	@echo "  make migrate   Run database migrations"
	@echo "  make seed      Seed default activities"
	@echo "  make dev       Start API server with hot reload"
	@echo "  make test      Run full test suite"
	@echo "  make backup    Run encrypted database backup"
	@echo "  make logs      Tail API logs"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python scripts/seed_activities.py

dev:
	cd backend && uvicorn main:app --host 0.0.0.0 --port 8080 --reload

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest tests/ -v

backup:
	bash scripts/backup.sh
