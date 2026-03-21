# Background Scheduler Documentation

## Overview

The Background Scheduler implements automated nightly analytics and insights generation using APScheduler. It runs daily at 11 PM (23:00) UTC to:

1. **Calculate Daily Stats** - Aggregate activity tracking data into daily summaries
2. **Detect Streaks** - Identify consecutive-day activity patterns and update streak counts
3. **Detect Correlations** - Analyze activity co-occurrence patterns (e.g., gym days → higher productivity)
4. **Detect Burnout** - Identify unhealthy patterns (high workload + low sleep)
5. **Generate Weekly Digest** - Create narrative summaries using AI (LLM)

## Architecture

```
FastAPI App Startup
    ↓
services/scheduler.py: start_scheduler()
    ↓
APScheduler BackgroundScheduler
    ↓
CronTrigger(hour=23, minute=0) → daily_analytics_job()
    ↓
┌─ calculate_daily_stats() ─ Parse events → Daily stats
├─ detect_streaks() ─ Check continuity → Update streak counts
├─ detect_correlations() ─ Analyze patterns → Log insights
├─ detect_burnout() ─ High work + low sleep → Create alerts
└─ generate_weekly_digest_job() ─ LLM summary → Store as memory
```

## Features

### 1. Daily Stats Calculation
**Purpose:** Convert hourly/minute-level event tracking into daily aggregates

**Logic:**
```python
for each event:
    if event.date == target_date:
        activity_totals[activity_id] += event.value

for activity_id, total in activity_totals.items():
    store_or_update(DailyStat, activity_id, target_date, total)
```

**Example Output:**
```
2024-01-15: coding_auto=480min, sleep=7h, exercise=30min
2024-01-14: coding_auto=420min, sleep=6h, exercise=0min
```

### 2. Streak Detection
**Purpose:** Track consecutive-day activity engagement

**State Transitions:**
```
NO STREAK
    ↓ (activity done today + yesterday)
ACTIVE STREAK (count increases each day)
    ↓ (activity NOT done today)
ENDED STREAK (frozen count, end_date set)
    ↓ (activity done again after break)
NEW STREAK (count resets to 1)
```

**Database Fields:**
- `start_date`: When streak began
- `current_count`: Days in active streak
- `longest_count`: Peak streak achieved
- `end_date`: When streak was broken (NULL if active)

**Example:**
```
Coding Streak:
  14 days (current) / 21 days (longest)
  Started: 2024-01-01
  Last: 2024-01-15

Meditation Streak:
  5 days (current) / 45 days (longest)
  Ended: 2024-01-12 (broke on 2024-01-13)
  New streak started: 2024-01-14
```

### 3. Correlation Detection
**Purpose:** Identify patterns between activities (e.g., exercise days correlate with better sleep)

**Current Implementation:** Basic co-occurrence analysis
- Groups daily stats by date
- Identifies days when multiple activities occur
- Logs patterns for manual review

**Future Enhancement:** Statistical correlation matrix using Pearson/Spearman coefficients

**Example Insights:**
```
- Gym days correlate with +2h more sleep (correlation: 0.68)
- High coding days correlate with -1.5h less exercise (correlation: -0.52)
- Social events correlate with better mood tracking scores (correlation: 0.74)
```

### 4. Burnout Detection
**Purpose:** Alert on unhealthy patterns (overwork without adequate recovery)

**Current Threshold:**
- High workload: > 8 hours coding/day
- Low sleep: < 6 hours/day
- Duration: 7+ consecutive days

**Trigger Condition:**
```python
if (daily_coding > 8 AND daily_sleep < 6) for 7+ days:
    create_alert(type="burnout_warning", message="...")
```

**Alert Example:**
```
Type: burnout_warning
Message: "High workload with insufficient sleep detected over 7 days. 
Consider reducing workload or improving sleep."
Created: 2024-01-15 23:00
```

**Future Enhancement:**
- Account for exercise/stress levels
- Self-reported mood tracking
- Graduated alert levels (warning → critical → override)
- Suggested recovery actions

### 5. Weekly Digest Generation
**Purpose:** AI-powered narrative summary of weekly activity

**Data Collection:**
- Aggregates 7 days of DailyStat records
- Groups by activity category
- Passes structured data to LLM

**LLM Prompt Structure:**
```
"Here is the user's data for the past week: {JSON data}

Write a personal, friendly weekly digest (3-4 paragraphs) that:
1. Summarises what went well
2. Highlights key patterns or correlations noticed
3. Gives 2-3 specific recommendations for next week
Write in second person (you/your). Be specific, not generic."
```

**Example Output:**
```
"You had a strong week focused on deep work! Your coding sessions averaged 9+ hours daily, 
which resulted in completing the authentication system ahead of schedule. However, I noticed 
your sleep dropped to 5-6 hours on work-intensive days. 

Positively, your weekend exercise routine added 3 sessions of 45+ minutes each, and you 
maintained your journaling habit 6 out of 7 days. 

For next week, I'd suggest:
1. Cap intensive coding sessions at 8 hours (add a 30-min walk break at 6 hours)
2. Aim for 7+ hours sleep on high-workload days—consider a 10pm bedtime
3. Continue weekend exercise—it's clearly giving you mental clarity"
```

**Storage:** Stored as Memory object with type="weekly_digest"

## Configuration

### Time & Schedule

**Default:** 11 PM UTC daily
**Location:** `services/scheduler.py` line ~150

To change schedule:
```python
# Change from CronTrigger(hour=23, minute=0) to:
CronTrigger(hour=20, minute=30)  # 8:30 PM
CronTrigger(minute=0)             # Every hour on the hour
CronTrigger(day_of_week='mon-fri', hour=9)  # Weekdays at 9 AM
```

### Environment Variables

```bash
# config.py
OLLAMA_HOST=http://localhost:11434  # LLM for weekly digest
EMBED_MODEL=all-MiniLM-L6-v2        # Embeddings for semantic search
```

### Database Requirements

Scheduler requires database tables:
- `activities` - Activity definitions
- `events` - Tracked activity events
- `daily_stats` - Daily aggregates (created by scheduler)
- `streaks` - Streak tracking
- `alerts` - Alert storage
- `journal_entries` - Journal (optional)
- `memories` - Memory storage (for weekly digest)

## Integration with FastAPI

**Startup:** `main.py` `@app.on_event("startup")`
```python
@app.on_event("startup")
async def startup_event():
    start_scheduler()
```

**Shutdown:** `main.py` `@app.on_event("shutdown")`
```python
@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()
```

**Catch-up:** First run calculates for today (prevents missing data if app restarted)

## API Interaction

### Endpoints That Feed Scheduler

**POST /api/track** - Submit activity event
- Scheduler reads these events at job time
- Creates DailyStat aggregates

**POST /api/track/batch** - Bulk upload from collectors
- Same: stored as events, aggregated at job time

### Endpoints That Use Scheduler Output

**GET /api/analytics/score** - Returns stats created by scheduler
**GET /api/streaks** - Returns streak data from scheduler
**GET /api/memory/query** - Can access weekly digests from memory store
**GET /api/alerts** - Returns burnout alerts from scheduler

## Testing

### Unit Tests
Location: `tests/test_scheduler.py`

**Test Categories:**
1. `TestDailyStatsCalculation` - Event aggregation
2. `TestStreakDetection` - Consecutive-day tracking
3. `TestBurnoutDetection` - Pattern identification
4. `TestCorrelationDetection` - Relationship analysis
5. `TestDailyAnalyticsJob` - Full job execution
6. `TestSchedulerLifecycle` - Start/stop operations

**Run Tests:**
```bash
pytest tests/test_scheduler.py -v
pytest tests/test_scheduler.py::TestDailyStatsCalculation -v
pytest tests/test_scheduler.py::TestBurnoutDetection::test_detect_burnout_triggers_alert -v
```

### Manual Testing

**Check Scheduler Status:**
```python
from services.scheduler import scheduler
print(scheduler.get_jobs())  # Lists scheduled jobs
```

**Trigger Job Manually:**
```python
from services.scheduler import daily_analytics_job
daily_analytics_job()  # Runs immediately
```

**View Logs:**
```bash
# Backend logs show scheduler output
docker logs backend  # Docker deployment
tail -f backend.log   # Local development
```

**Expected Log Output:**
```
=== Daily Analytics Job Starting ===
Calculating daily stats for 2024-01-15
Daily stats calculated: 8 activities
Detecting streaks as of 2024-01-15
Streaks updated for 12 activities
Detecting correlations over last 30 days
Analyzed 30 days of data for patterns
Checking for burnout patterns in last 7 days
No burnout pattern detected (3/7 threshold days)
Generating weekly digest
Weekly digest generated and stored
=== Daily Analytics Job Completed ===
```

## Troubleshooting

### Scheduler Not Starting

**Issue:** "Could not start scheduler"

**Solution:**
1. Check APScheduler installed: `pip list | grep APScheduler`
2. Verify database connection: Check PostgreSQL running
3. Check logs for detailed error

### Job Not Running At Scheduled Time

**Issue:** 11 PM passes but job doesn't execute

**Possibilities:**
1. **App not running** - Backend must stay running for scheduler
2. **Timezone mismatch** - Check UTC vs local time
3. **Scheduler crashed** - Check logs
4. **Job failed silently** - Add logging to job functions

**Solution:**
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
```

### Database Connection Errors during Job

**Issue:** Job fails with "database connection refused"

**Causes:**
- PostgreSQL down during scheduled time
- Connection pool exhausted
- Long-running queries blocking

**Solution:**
```python
# Add retry logic in scheduler
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def daily_analytics_job():
    db = get_db()
    try:
        # ... job code ...
    finally:
        db.close()
```

### High Memory Usage

**Issue:** Backend process memory grows over time

**Cause:** Embeddings model or session leaks

**Solution:**
1. Add `db.close()` after every job task
2. Limit memory usage: `scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(max_workers=1)})`

### Performance: Job Takes Too Long

**Issue:** Job runs longer than scheduled interval

**Current Default:** Daily job at 11 PM = 24 hours between runs (safe)

**Optimization Options:**
```python
# 1. Run specific tasks instead of all
# - Separate streak detection to different time
# - Run correlation analysis only 1x/week

# 2. Add indexing to database
# - Index on (date, activity_id) for DailyStat queries
# - Index on created_at for Memory retrieval

# 3. Limit data scope
# - Only analyze last 30 days instead of all history
# - Increase batch size for bulk updates
```

## Future Enhancements

### Planned Features
1. **Micro-habit Tracking** - Recognize small positive streaks
2. **Predictive Alerts** - "You're heading toward burnout based on last 3 days"
3. **Goal Progress Tracking** - Weekly goal achievement rate
4. **Personalized Recommendations** - "Based on your patterns, best time to work is 7-10 AM"
5. **Export Weekly Digest** - Email or calendar export

### Advanced Analytics
1. **Seasonality Analysis** - Detect yearly patterns
2. **Anomaly Detection** - Alert on unusual activity deviations
3. **Causal Analysis** - "Earlier sleep → higher productivity (correlation: 0.82)"
4. **Activity Recommendations** - Suggest new activities based on interests

### Multi-User Enhancements
1. **Per-User Schedules** - Different notification times per user timezone
2. **Team Analytics** - Compare patterns across team members (with permission)
3. **Custom Job Configurations** - User-editable burnout thresholds

## Implementation Checklist

- [x] Create scheduler.py with APScheduler integration
- [x] Create daily_analytics_job() orchestrator
- [x] Implement calculate_daily_stats()
- [x] Implement detect_streaks()
- [x] Implement detect_correlations()
- [x] Implement detect_burnout()
- [x] Implement weekly_digest generation
- [x] Integrate with FastAPI startup/shutdown
- [x] Add logging throughout
- [x] Create comprehensive test suite
- [ ] Deploy to production
- [ ] Monitor job execution
- [ ] Gather user feedback
- [ ] Implement enhancements

## Quick Start

1. **Backend is already running** with scheduler integrated

2. **First job runs at 11 PM UTC tonight**

3. **To test immediately:**
   ```bash
   python -c "from backend.services.scheduler import daily_analytics_job; daily_analytics_job()"
   ```

4. **View results:**
   - Check database: `SELECT * FROM daily_stats WHERE date = TODAY()`
   - Check streaks: `SELECT * FROM streaks ORDER BY updated_at DESC`
   - Check alerts: `SELECT * FROM alerts WHERE type='burnout_warning'`
   - Check memories: `SELECT * FROM memories WHERE type='weekly_digest'`

---

**Created:** 2024-01-15
**Status:** Implemented and tested
**Next Priority:** Integration tests for full data flow
