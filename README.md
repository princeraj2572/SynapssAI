# Personal Life OS

> **Your private, AI-powered operating system for life.**
> Track everything. Understand everything. All on your machine.

---

## What is this?

Personal Life OS automatically captures data from every app, device, and activity — coding sessions, Git commits, sleep, gym, mood, screen time, study hours — stores it all locally in PostgreSQL, and uses a local LLM (Llama 3 via Ollama) to help you understand your patterns and get personalized coaching. Zero cloud. Zero data sharing. Everything runs on your machine.

## Features

- **Automatic tracking** — desktop agent, browser extension, Git scanner
- **Manual logging** — CLI tool and one-click dashboard buttons
- **Streak detection** — daily/weekly streaks for every activity
- **Correlation discovery** — automatically finds patterns (e.g. "gym days → +40% coding")
- **Burnout detection** — alerts when high workload + low sleep patterns emerge
- **Productivity scoring** — weighted daily score (0–100) across all activities
- **AI Coach** — ask questions about your life in natural language, powered by local LLM
- **Weekly digest** — LLM-generated narrative of your week
- **Full privacy** — localhost only, no telemetry, no third-party services

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL 16 + pgvector |
| AI / LLM | Ollama + Llama 3.1 8B |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Frontend | Next.js 14, React, TypeScript, Tailwind, Recharts |
| Collectors | Python (desktop), JS WebExtension (browser), Kotlin (Android) |
| Scheduler | APScheduler (nightly analytics jobs) |

## Quick Start (Windows)

### Prerequisites
- Python 3.10+, Node.js 18+, PostgreSQL 16, Git

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/personal-life-os.git
cd personal-life-os
copy .env.example .env
# Edit .env — set your PostgreSQL password
```

### 2. Set up PostgreSQL

```bash
psql -U postgres
```
```sql
CREATE DATABASE lifedb;
\c lifedb
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 3. Set up backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python db\init_db.py
python ..\scripts\seed_activities.py
```

### 4. Start the API server

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Visit: http://localhost:8080/docs

### 5. Set up frontend

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

### 6. Start tracking

**Desktop agent** (tracks your active window automatically):
```bash
cd collectors/desktop
pip install -r requirements.txt
python agent.py
```

**Browser extension:**
1. Open Chrome → chrome://extensions
2. Enable "Developer mode"
3. Click "Load unpacked" → select `collectors/browser-extension/`

**Git scanner:**
```bash
cd collectors/git-scanner
python scanner.py --root C:\Users\yourname\projects
```

**Manual logging via CLI:**
```bash
cd collectors/manual-logger
python cli.py mood 4
python cli.py sleep 7.5
python cli.py gym 1 "leg day"
python cli.py coding 3 "worked on auth"
```

### 7. AI Coach (optional)

```bash
# Install Ollama from https://ollama.com
ollama pull llama3.1:8b
ollama serve
```

Then open http://localhost:3000/chat and ask anything.

## Running Tests

```bash
cd backend
venv\Scripts\activate
pip install pytest
pytest ../tests/ -v
```

## Project Structure

```
personal-life-os/
├── backend/          # FastAPI server, models, services, jobs
├── frontend/         # Next.js dashboard (9 pages)
├── collectors/       # Desktop agent, browser extension, git scanner
├── scripts/          # Setup, seed, backup utilities
├── tests/            # pytest test suite
└── docs/             # Documentation
```

## License

Personal Life OS is open source under the **AGPL v3** license — free for personal use and self-hosting.

For commercial use or to remove AGPL obligations, a commercial license is available.
Contact: your@email.com

## Roadmap

- [ ] Android app (Kotlin — UsageStats + steps)
- [ ] Wearable sync (Garmin, Apple Health, Oura)
- [ ] pgvector semantic search (upgrade from keyword search)
- [ ] Habit prediction (ARIMA / Prophet)
- [ ] Calendar sync (iCal import)
- [ ] Encrypted multi-device sync (Syncthing)
- [ ] Docker Compose one-command setup

---

Built with privacy first. Your data never leaves your machine.
