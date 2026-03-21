# Setup Guide

## Prerequisites
- Python 3.12+
- Node.js 22+
- Docker Desktop
- PostgreSQL 16 (or use Docker)
- Git

## Quick start (Docker — recommended)
```bash
cp .env.example .env
docker compose up -d
# Wait ~30 seconds for postgres to initialise
python scripts/seed_activities.py
# Open http://localhost:3000
```

## Manual start (no Docker)
```bash
# 1. Start PostgreSQL and create DB
createdb lifedb
psql lifedb -c 'CREATE EXTENSION IF NOT EXISTS vector;'

# 2. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8080

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev

# 4. Seed activities
python ../scripts/seed_activities.py
```
