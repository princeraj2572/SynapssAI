# Life OS Collectors

This directory contains all data collection agents that feed activity data into your Personal Life OS.

## Overview

Collectors run independently and asynchronously, sending activity events to the backend API via HTTP. They all follow the same pattern:

1. **Detect** → Capture activity (window, website, commit, manual log)
2. **Categorize** → Map raw data to activity categories
3. **Buffer** → Accumulate events locally
4. **Send** → Batch send to API at `http://localhost:8080/api/track/batch`

All collectors respect local storage and **never send data outside your machine**.

---

## Available Collectors

### 1. Desktop Agent

**Purpose:** Automatic background tracking of active windows and idle time.

**Location:** `./desktop/`

**Setup:**
```bash
cd desktop
pip install -r requirements.txt
python agent.py
```

**What it tracks:**
- Active application and window title
- Time spent in each app
- Idle periods (configurable threshold)
- Automatic categorization (coding, browser, communication, etc.)

**Configuration:** Edit `config.yaml`
```yaml
api_url: http://localhost:8080          # Backend API endpoint
poll_interval_seconds: 10                # How often to check active window
idle_threshold_seconds: 180              # Idle = no mouse/keyboard for this duration
batch_every_seconds: 60                  # How often to send batches to API
```

**Categories auto-detected:**
- **Coding**: VS Code, PyCharm, terminal, vim, etc.
- **Browser**: Chrome, Firefox, Safari, Edge, etc.
- **Communication**: Slack, Discord, Teams, Zoom, etc.
- **Productivity**: Notion, Figma, Excel, Word, etc.
- **Entertainment**: Netflix, Spotify, Steam, VLC, etc.
- **Other**: Everything else

**Output format:**
```json
{
  "activity": "coding_auto",
  "value": 1.5,
  "start": "2024-03-22T14:30:00Z",
  "end": "2024-03-22T16:00:00Z",
  "source": "desktop_agent",
  "notes": "vscode: main.py - Personal Life OS"
}
```

**Tips:**
- Run at Windows startup to capture all-day data
- Press `Ctrl+C` to pause tracking anytime
- Logs go to console — redirect to file with `> agent.log 2>&1`
- Requires admin privileges on Windows for full window detection

**Troubleshooting:**
- **"Permission denied"** → Run as Administrator
- **"Window is Unknown"** → App hides window title; try categorizing manually
- **API connection errors** → Ensure backend is running on `:8080`

---

### 2. Browser Extension

**Purpose:** Track websites visited, time per domain, and form submissions (searches, logins, etc.)

**Location:** `./browser-extension/`

**Chrome Installation:**
1. Open `chrome://extensions`
2. Toggle **Developer mode** (top-right)
3. Click **Load unpacked**
4. Select this folder
5. Grant all requested permissions

**Firefox Installation:**
1. Open `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on**
3. Select `manifest.json`

**What it tracks:**
- Domain and time spent
- Page title (optional, can disable in settings)
- Search queries (Google, Bing, DuckDuckGo)
- YouTube watch history
- Form submissions

**Output format:**
```json
{
  "activity": "browser_time",
  "value": 0.5,
  "start": "2024-03-22T14:30:00Z",
  "end": "2024-03-22T15:00:00Z",
  "source": "browser_extension",
  "notes": "github.com - GitHub: Build software better"
}
```

**Configuration options:**
- Click extension icon → Options
- Pause/resume tracking
- Whitelist domains (no tracking)
- Blacklist domains (don't report specific sites)
- Toggle YouTube tracking
- Toggle search query capture

**Tips:**
- Extension syncs every 5 minutes
- Pause during private browsing
- Whitelist banking sites for privacy
- Custom domain mappings in settings

---

### 3. Git Scanner

**Purpose:** Automated scanning of Git repositories to infer coding time from commit history.

**Location:** `./git-scanner/`

**Setup:**
```bash
cd git-scanner
pip install -r requirements.txt
python scanner.py --root "C:\Users\YourName\projects"
```

**Scan multiple folders:**
```bash
python scanner.py --root "C:\code" "D:\work" "E:\hobby-projects"
```

**What it tracks:**
- Commits per project per day
- Coding time (inferred from commit timestamps)
- Project names and languages
- Commit authors and messages

**Output format:**
```json
{
  "activity": "coding_auto",
  "value": 2.5,
  "start": "2024-03-22T09:00:00Z",
  "end": "2024-03-22T11:30:00Z",
  "source": "git_scanner",
  "notes": "personal-life-os: frontend redesign (3 commits)"
}
```

**Configuration:**
- Create `.last_scan.json` to cache results
- Setup automated daily runs via Task Scheduler:
  ```bash
  # Windows Task Scheduler: 
  # Run daily at 11:59 PM: python scanner.py --root C:\Users\YourName\projects
  ```

**Tips:**
- First scan indexes all history — subsequent scans are fast
- Run after major coding sessions for accuracy
- Combine with desktop agent for complete picture
- Skip repos by adding `private = true` to `.git/config`

---

### 4. Manual Logger

**Purpose:** Quick CLI tool for logging activities that aren't automatically tracked.

**Location:** `./manual-logger/`

**Basic usage:**
```bash
cd manual-logger

# Log mood (1-5 scale)
python cli.py mood 4

# Log sleep hours
python cli.py sleep 7.5

# Log workout with duration
python cli.py gym 1.5 "leg day"

# Log reading time
python cli.py reading 45 "finished chapter 3"

# Log custom activity
python cli.py meditation 20 "morning session"
```

**Supported formats:**
- `python cli.py <activity> <value>`
- `python cli.py <activity> <value> "<notes>"`
- Value can be: `5`, `7.5`, `45 minutes`, `2 hours`, `1.5`

**Default activities:**
- `mood` (1-5)
- `sleep` (hours)
- `exercise`, `gym`, `yoga`, `meditation` (minutes)
- `coding`, `writing`, `reading` (hours)
- `water` (glasses), `coffee` (cups)

**Create custom activities:**
1. Open http://localhost:3000/settings
2. Click "Add Custom Activity"
3. Enter name, category, unit
4. Use immediately: `python cli.py <name> <value>`

**PowerShell alias for faster logging:**
```powershell
Set-Alias -Name log -Value "python C:\path\to\manual-logger\cli.py"
log mood 5
log sleep 8
log gym 1.5
```

**Tips:**
- Log immediately after activity for accuracy
- Use `45 minutes` or `1.5` for flexibility
- Notes are optional but recommended
- Can bulk-import past data via CSV

---

### 5. Wearable Sync (Coming Soon)

**Purpose:** Sync sleep, steps, heart rate from fitness trackers.

**Supported devices:**
- Garmin Connect API (coming Q2 2024)
- Apple Health (coming Q2 2024)
- Oura Ring (coming Q3 2024)
- Fitbit (coming Q3 2024)

**What it will track:**
- Daily sleep duration and quality
- Steps and active minutes
- Heart rate and HRV
- Workouts and calorie burn

---

### 6. Calendar Sync (Coming Soon)

**Purpose:** Sync calendar events to track meetings and dedicated time blocks.

**Supported calendars:**
- Google Calendar
- Outlook / Office 365
- iCal (.ics files)

**What it will track:**
- Meeting duration and attendees
- Focus blocks and free time
- Travel time

---

## Running Multiple Collectors

You can run all collectors simultaneously in separate processes:

```bash
# Terminal 1: Desktop Agent
cd collectors/desktop && python agent.py

# Terminal 2: Git Scanner (daily scheduled via Task Scheduler is better)
cd collectors/git-scanner && python scanner.py --root "C:\Users\YourName\projects"

# Terminal 3: Browser Extension (runs continuously if loaded)
# Just keep Chrome with extension running

# Terminal 4: Manual Logger (use as needed)
cd collectors/manual-logger && python cli.py mood 4
```

Or use a batch script to manage them:

```batch
@echo off
start "Desktop Agent" cmd /k "cd collectors\desktop && python agent.py"
start "Browser Extension" chrome.exe
echo Collectors started. Manual logger available: cd collectors\manual-logger && python cli.py mood 4
```

---

## Testing Collectors

Run the test suite:
```bash
cd ..
pip install pytest
pytest tests/test_desktop_collector.py -v
```

Test data flow:
1. Start backend: `cd backend && uvicorn main:app --port 8080`
2. Start a collector: `cd collectors/desktop && python agent.py`
3. Check logs in backend console
4. View data in dashboard: http://localhost:3000

---

## Data Flow Architecture

```
Desktop App Window → Desktop Agent → Buffer → Batch Send
                                           ↓
                                    API Endpoint
                                           ↓
                                      Validate
                                           ↓
                                      Store in DB
                                           ↓
                                    Dashboard View
```

**All collectors** follow this pattern:
1. Capture event locally
2. Add to buffer (no immediate API call)
3. Every `batch_interval` seconds → HTTP POST to `/api/track/batch`
4. Backend validates and stores in PostgreSQL
5. Available on dashboard instantly

---

## Privacy & Security

✅ **All collectors:**
- Store data locally only — never cloud sync
- Connect to localhost only — no external API calls
- Can pause/disable anytime with `Ctrl+C`
- No telemetry or tracking of usage
- No login required — all local

**To audit:**
1. Check `config.yaml` — only `localhost:8080` in API URL
2. Desktop agent uses only local Python libraries
3. Browser extension scopes to `localhost` only
4. Manual logger never sends data elsewhere
5. Git scanner reads local `.git` directories only

---

## Troubleshooting

**Desktop agent shows "Unknown" apps:**
- Some apps hide window titles (terminals, certain browsers)
- Open Settings → Add Custom Activity → manually categorize
- Report app name to add to categorizer

**Browser extension not capturing:**
- Check it's enabled in `chrome://extensions`
- Ensure it has "All sites" permission
- Try reloading extension
- Check for Content-Security-Policy headers blocking it

**Git scanner missing repos:**
- Ensure you provided correct root folder path
- Check that `.git` folders aren't in `.gitignore`
- Verify no permission errors on folders

**Manual logger command not found:**
- Add full path: `python C:\path\to\cli.py mood 4`
- Create PowerShell alias (see above)
- Ensure Python is in PATH

**API connection errors:**
- Check backend is running: `curl http://localhost:8080/docs`
- Check no firewall blocking localhost:8080
- Restart backend and collectors
- Check in backend logs for errors

---

## Contributing

To add a new collector:
1. Create folder in `/collectors/<name>/`
2. Implement `main.py` or `agent.py`
3. Add `requirements.txt` with dependencies
4. Implement event sending via `requests.post` to API
5. Add tests in `/tests/test_<name>_collector.py`
6. Update this README with usage instructions
7. Submit PR

**Collector guidelines:**
- Use standard event format (activity, value, start, end, source, notes)
- Buffer events and batch send (don't send on every event)
- Handle API connection errors gracefully
- Log significant events (startup, batches sent, errors)
- Make configuration simple (YAML or env vars, not code)

