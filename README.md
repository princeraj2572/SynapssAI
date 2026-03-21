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

Choose one or more trackers based on your needs. You can run multiple collectors simultaneously.

#### **Desktop Agent** (Automatic window tracking)
Runs in the background and automatically logs your active window every minute.

```bash
cd collectors/desktop
pip install -r requirements.txt
python agent.py
```

**What it tracks:**
- Active application and window title
- Time spent in each app/project
- Idle periods (no mouse/keyboard activity)
- Matches projects against your Git repos for coding session detection

**Tips:**
- Run at startup: Add `pythonw agent.py` to Windows Task Scheduler or startup folder
- Disable for privacy: Press `Ctrl+C` to pause anytime
- Configure in `config.yaml`: Set Git repo paths, idle threshold, ignored apps
- First sync may take time if you have many Git repos

**Troubleshooting:**
- If window detection fails, ensure the app runs with admin privileges
- On multi-monitor setups, it tracks the active monitor only
- Some apps hide window titles (e.g., browsers, terminals) — detection may be generic

---

#### **Browser Extension** (Web activity tracking)
Tracks websites visited, time spent per domain, and captures form submissions (search queries, etc.).

**Chrome Installation:**
1. Open `chrome://extensions`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the `collectors/browser-extension/` folder
5. Grant permissions when prompted

**Firefox Installation (if supported):**
1. Open `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Select `collectors/browser-extension/manifest.json`

**What it tracks:**
- Domain visited and time spent
- Page titles and URLs (optional, configurable)
- Search queries (Google, Bing, DuckDuckGo)
- YouTube watch history
- Form submissions

**Tips:**
- Click the extension icon to pause/resume tracking
- Visit extension options to whitelist domains or disable tracking for certain sites
- YouTube time is categorized as "screen-entertainment" by default — edit custom activities to change
- Logs sync every 5 minutes automatically

---

#### **Git Scanner** (Coding session tracking)
Scans your Git repositories and logs commits with time spent coding based on commit frequency.

```bash
cd collectors/git-scanner
python scanner.py --root C:\Users\yourname\projects
```

Or scan multiple folders:
```bash
python scanner.py --root "C:\code" "D:\work" "E:\side-projects"
```

**What it tracks:**
- Commits per day, per project
- Time spent coding (inferred from commit timestamps)
- Projects and languages worked on
- Author and commit messages

**Setup:**
- Provide the root folder(s) where your Git repos are located
- Scanner will discover all `.git` directories recursively
- First run will index all history — subsequent runs are fast

**Tips:**
- Run daily via cron (Linux/Mac) or Task Scheduler (Windows):
  ```bash
  # Windows Task Scheduler: Add a task to run at 11:59 PM daily
  python C:\path\to\scanner.py --root C:\Users\yourname\projects
  ```
- Combine with desktop agent for complete picture of coding time
- Skips private repos (`.git/config` contains `private = true`)

**Supported Git services:**
- GitHub, GitLab, Bitbucket (local clones)
- Self-hosted Git servers

---

#### **Manual Logging via CLI** (Quick activity entry)
Log activities instantly from the command line.

```bash
cd collectors/manual-logger

# Log mood (1-5 scale)
python cli.py mood 4

# Log hours of sleep
python cli.py sleep 7.5

# Log workout with duration and notes
python cli.py gym 1 "leg day"
python cli.py exercise 45 minutes "30 min run, 15 min weights"

# Log coding session with notes
python cli.py coding 3 "worked on auth system"

# Log custom activity (if created in settings)
python cli.py meditation 20 "morning session"
```

**Supported formats:**
- `python cli.py <activity> <value> [optional notes]`
- Value can be: number (`5`), decimal (`7.5`), time (`45 minutes`, `2 hours`)
- Notes are optional but recommended for context

**Auto-created activities (default config):**
- `mood` (1-5 scale)
- `sleep` (hours)
- `exercise`, `gym`, `yoga`, `meditation` (minutes)
- `coding`, `writing`, `reading` (hours)
- `water` (glasses), `coffee` (cups)

**Create custom activities in the dashboard:**
- Open http://localhost:3000/settings
- Scroll to "Add Custom Activity"
- Enter name, category, and unit
- Log via CLI immediately: `python cli.py <name> <value>`

**Tips:**
- Create a PowerShell alias for faster logging:
  ```powershell
  Set-Alias -Name log -Value "python C:\path\to\collectors\manual-logger\cli.py"
  log mood 4
  ```
- Log immediately after an activity (best for accuracy)
- Bulk import past data: Edit `manual_entries.csv` in the collectors folder

---

#### **Dashboard Quick Actions** (Web UI logging)
Log activities directly from the dashboard without leaving your browser.

1. Open http://localhost:3000
2. Scroll to **Quick Actions**
3. Click activity buttons to log instantly
4. View confirmation message with CheckCircle icon

**Features:**
- One-click logging — no typing required
- Instant feedback with success message
- Pre-configured with most common activities
- Add custom activities in Settings

---

#### **Wearable Sync** (Sleep, steps, heart rate)
*(Optional — requires wearable device)*

Currently under development. Supported wearables:
- **Garmin** — via Garmin Connect API
- **Apple Health** — via iPhone companion app (coming soon)
- **Oura Ring** — via Oura Cloud API (coming soon)
- **Fitbit** — via Fitbit Web API (coming soon)

---

### Tips for Effective Tracking

1. **Start simple** — Begin with 1-2 trackers (e.g., desktop agent + manual mood logging)
2. **Run multiple trackers** — Desktop + browser + git scanner gives maximum insight
3. **Be consistent** — Daily manual logging (even quick entries) compounds over time
4. **Set a schedule:**
   - Morning: Log mood + sleep quality
   - Evening: Log gym, meals, reading time
   - End of day: Quick summary via dashboard
5. **Review weekly** — Visit the dashboard every Sunday to spot patterns
6. **Create custom activities** — Add things unique to you (e.g., "violin practice", "journaling")
7. **Use the AI Coach** — Ask questions after 2 weeks of data (http://localhost:3000)

---

### Data Sync & Storage

- **All data stored locally** in PostgreSQL at `~/.personal-life-os/lifedb`
- **Automatic sync** between collectors and API (every 5-10 minutes)
- **No cloud sync** — only your machine has your data
- **Backup recommended** — Run `./scripts/backup.sh` weekly

---

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
