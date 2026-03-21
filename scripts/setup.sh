#!/bin/bash
set -e
echo "=== Personal Life OS — First-time Setup ==="

# Copy env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — edit it with your settings."
fi

# Python deps
echo "Installing Python dependencies..."
cd backend && pip install -r requirements.txt && cd ..

# Node deps
echo "Installing Node dependencies..."
cd frontend && npm install && cd ..

# Start only postgres
echo "Starting PostgreSQL..."
docker compose up -d postgres
sleep 5

# Run migrations
echo "Running DB migrations..."
cd backend && python -m alembic -c db/alembic.ini upgrade head && cd ..

# Seed activities
echo "Seeding default activities..."
python scripts/seed_activities.py

echo ""
echo "=== Setup complete! Run: make dev ==="
