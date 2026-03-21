# Integration Tests Documentation

## Overview

Integration tests validate end-to-end data flows across the Personal Life OS system, from data collection through analytics to AI insights. These tests ensure all components work together correctly.

**Location:** [tests/test_integration.py](tests/test_integration.py)
**Framework:** pytest with async/httpx support
**Test Count:** 25+ integration tests organized in 8 test classes

## Test Architecture

```
Integration Tests (test_integration.py)
│
├── Setup Fixtures
│   ├── client (AsyncClient for API)
│   ├── db (Database session)
│   └── setup_activities (Standard activities: coding, sleep, exercise, etc.)
│
├── TestTrackingPipeline (2 tests)
│   ├── Single event tracking
│   └── Batch event tracking
│
├── TestAnalyticsPipeline (3 tests)
│   ├── Daily stats aggregation
│   ├── Streak detection
│   └── Analytics endpoint usage
│
├── TestMemoryAndChatPipeline (2 tests)
│   ├── Daily memory generation
│   └── Memory query endpoint
│
├── TestBurnoutDetectionPipeline (2 tests)
│   ├── Burnout alert generation
│   └── Alerts endpoint
│
├── TestActivityTrackingWorkflow (1 test)
│   └── Complete activity lifecycle
│
├── TestJournalIntegration (2 tests)
│   ├── Journal entry storage
│   └── Journal query retrieval
│
├── TestDataConsistency (2 tests)
│   ├── Activity cascade deletion
│   └── Stats match event aggregates
│
└── TestEndToEndPipeline (1 test)
    └── Full daily workflow
```

## Test Classes

### 1. TestTrackingPipeline
Tests data collection and storage mechanisms.

**Tests:**
- `test_single_event_tracking` - Verify single event submission works and stores correctly
- `test_batch_tracking_events` - Verify batch submission and aggregation

**Flow:**
```
POST /api/track (single)    → Event object → Database
POST /api/track/batch       → Multiple events → Daily stats calculation
```

**Validation:**
- Event count matches submission
- Daily stats aggregated correctly
- Health endpoint responsive

### 2. TestAnalyticsPipeline
Tests calculation of insights from raw data.

**Tests:**
- `test_daily_stats_aggregation_pipeline` - Events aggregate into daily totals
- `test_streak_detection_pipeline` - Consecutive days detected correctly
- `test_analytics_endpoint_uses_calculated_data` - Endpoint returns calculated data

**Flow:**
```
Events (multiple per day) 
    → calculate_daily_stats()
    → DailyStat records (1 per activity per day)

DailyStat records (consecutive days)
    → detect_streaks()
    → Streak records (with current_count, longest_count)

Analytics endpoint
    → Returns aggregated data for visualization
```

**Example:**
```python
# 4 coding events of 100 minutes each
Event(activity_id=1, value=100)  # 10:00
Event(activity_id=1, value=100)  # 10:30
Event(activity_id=1, value=100)  # 14:00
Event(activity_id=1, value=100)  # 15:00

calculate_daily_stats()
    ↓
DailyStat(activity_id=1, date=today, total_value=400)

# 3 days of data
detect_streaks()
    ↓
Streak(activity_id=1, current_count=3, longest_count=3)
```

### 3. TestMemoryAndChatPipeline
Tests LLM integration for memory and semantic search.

**Tests:**
- `test_daily_memory_generation` - Convert stats to natural language memory
- `test_memory_query_endpoint` - Query memory with semantic search

**Flow:**
```
DailyStat (structured data)
    → generate_daily_memory()
    → "On 2024-01-15: coding 480 min, sleep 7h"

Memory records (historical)
    → Memory query endpoint
    → LLM + semantic search
    → RAG-enhanced response
```

**Example:**
```python
# Stats from database
DailyStat(activity_id=1, date=2024-01-15, total_value=480)

# Generates natural language
"On 2024-01-15: coding_auto: 480 minutes, sleep: 7 hours"

# Stores as memory
Memory(type="daily_summary", content="On 2024-01-15...")

# User queries
POST /api/memory/query {"query": "How much did I code recently?"}
    ↓
Semantic search finds relevant memories
    ↓
LLM generates contextualized response
```

### 4. TestBurnoutDetectionPipeline
Tests burnout pattern detection and alerting.

**Tests:**
- `test_burnout_alert_generation` - High work + low sleep → Alert
- `test_alerts_endpoint_shows_burnout_warnings` - Alerts accessible via API

**Flow:**
```
7+ days of:
    - coding > 8 hours AND
    - sleep < 6 hours
    
    ↓
detect_burnout()
    ↓
Alert(type="burnout_warning", message="...")
    ↓
GET /api/alerts (returns all alerts including burnout)
```

**Threshold:** 
- Burnout alert triggers if ALL of 7 consecutive days meet both conditions
- Can be customized: `detect_burnout(db, threshold_days=5)`

### 5. TestActivityTrackingWorkflow
Tests complete activity lifecycle.

**Tests:**
- `test_create_custom_activity` - Create → Track → Retrieve

**Flow:**
```
POST /api/activities → New activity created

Event(activity_id=new_id, value=120)
    ↓
Stored in database

GET /api/analytics → Activity data included
```

### 6. TestJournalIntegration
Tests journaling features alongside activity tracking.

**Tests:**
- `test_journal_entry_storage` - Store journal entries
- `test_journal_query_retrieval` - Retrieve journal data

**Flow:**
```
POST /api/journal
    {
        "content": "Had a productive day",
        "mood": 8,
        "energy": 7,
        "tags": ["productive", "coding"]
    }
    ↓
Journal entry stored

GET /api/journal
    ↓
Returns journal entries (optionally filtered by date)
```

### 7. TestDataConsistency
Tests data integrity and logical consistency.

**Tests:**
- `test_activity_deletion_cascades_correctly` - Deleting activity removes related data
- `test_stats_match_event_aggregates` - Stats totals equal sum of events

**Data Integrity Checks:**
```python
# Events aggregate correctly
sum(event.value for event in events) == daily_stat.total_value

# Streaks track continuity
if daily_stat[today].value > 0 and daily_stat[yesterday].value > 0:
    streak.current_count += 1

# No orphaned records
if activity.deleted:
    event.deleted should cascade
    daily_stat.deleted should cascade
```

### 8. TestEndToEndPipeline
Complete workflow simulation from start to finish.

**Tests:**
- `test_full_daily_workflow` - Track → Stats → Streaks → Consistent

**Workflow Simulation:**
```
1. Simulate tracking (create 5 events: 100 min each)
2. Calculate daily stats (500 total min)
3. Setup previous day data (300 min)
4. Detect streaks (count = 2 consecutive days)
5. Verify all data consistent and linked
```

**Validates:**
- Data flows through entire pipeline
- All components correctly integrated
- Stats match event sums
- Streaks correctly calculated
- No broken links or missing references

## Running Tests

### Run All Integration Tests
```bash
pytest tests/test_integration.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_integration.py::TestAnalyticsPipeline -v
```

### Run Specific Test
```bash
pytest tests/test_integration.py::TestBurnoutDetectionPipeline::test_burnout_alert_generation -v
```

### Run with Coverage
```bash
pytest tests/test_integration.py --cov=backend --cov-report=html
```

### Run Async Tests Only
```bash
pytest tests/test_integration.py -m asyncio -v
```

## Test Dependencies

**Fixtures (Automatic Setup):**
- `client` - AsyncClient connected to test app
- `db` - Clean database session for each test
- `setup_activities` - Pre-created standard activities

**Models Required:**
- Activity, Event, DailyStat, Streak
- Memory, Journal, Alert
- All models must support database operations

**Services Required:**
- `calculate_daily_stats()` from scheduler
- `detect_streaks()` from scheduler
- `generate_daily_memory()` from memory service
- Database session management

## Expected Test Results

### Passing Criteria
- ✅ All events stored correctly
- ✅ Stats aggregation accurate
- ✅ Streaks detect consecutive days
- ✅ Burnout alerts trigger on threshold
- ✅ Memory generation produces text
- ✅ Endpoints return correct status codes
- ✅ Data consistency validated

### Common Issues

**Issue: Database not initialized**
```
Error: No such table: activities
Solution: Run db.init_db.py or ensure test database has all tables
```

**Issue: AsyncIO timeout**
```
Error: asyncio._exceptions.TimeoutError
Solution: Increase timeout in test, or check LLM/Ollama is running
```

**Issue: Memory foreign key constraint**
```
Error: Foreign key violation when creating Memory
Solution: Create activity first, then event with activity_id
```

**Issue: Episode isolation failure**
```
Error: Database contains data from previous test
Solution: Each test should have fresh db fixture (auto-cleaned)
```

## Integration Test Scenarios

### Scenario 1: Desktop Collector → API → Analytics
```
Desktop agent collects 8 hours coding
    → POST /api/track/batch
    → Events stored in database
    → Scheduler calculates daily stats
    → Analytics endpoint shows 480 minutes
    → Memory generated: "8 hours coding"
```

**Test:** `test_batch_tracking_events` + `test_daily_stats_aggregation_pipeline`

### Scenario 2: Multi-Day Streak Recognition
```
Day 1: User codes 5 hours
Day 2: User codes 6 hours  
Day 3: User codes 7 hours
    → Scheduler detects streak
    → Streak count = 3, longest = 3
    → No alert (healthy pattern)
```

**Test:** `test_streak_detection_pipeline`

### Scenario 3: Burnout Alert Generation
```
Days 1-7: User works 10+ hours, sleeps 5 hours
    → Scheduler detects pattern
    → Alert(type="burnout_warning") created
    → Alert appears in /api/alerts
    → User sees warning in dashboard
```

**Test:** `test_burnout_alert_generation`

### Scenario 4: Journal + Activity Correlation
```
User logs journal: "exhausted, couldn't exercise"
    + Data shows: 12h work, 4h sleep
    → Memory system correlates: overwork → missing exercise
    → LLM generates: "Your exercise routine broke this week due to high workload"
    → Recommendation: "Prioritize 30-min walks for mental health"
```

**Test:** `test_journal_entry_storage` + `test_memory_query_endpoint`

## Coverage Goals

**Target Coverage:** 80%+ of backend services
**Key Areas Covered:**
- ✅ Tracking pipeline (events → storage)
- ✅ Analytics pipeline (events → stats → insights)
- ✅ Memory system (data → semantic retrieval → LLM)
- ✅ Burnout detection (pattern → alert)
- ✅ Data consistency (CRUD operations)
- ✅ API endpoints (all main routes)

**Areas NOT Covered (Unit Tests Preferred):**
- ❌ Authentication/Authorization
- ❌ Error recovery/retry logic
- ❌ Performance benchmarks
- ❌ Database migrations
- ❌ External API calls (require mocking)

## Continuous Integration

**CI Pipeline Integration:**
```yaml
# .github/workflows/tests.yml
on: [push, pull_request]
jobs:
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: lifedb_test
          POSTGRES_PASSWORD: test
    steps:
      - uses: actions/checkout@v2
      - name: Run integration tests
        run: pytest tests/test_integration.py -v --tb=short
```

## Performance Metrics

**Expected Test Run Times:**
- Full suite: 30-60 seconds
- Single test class: 5-15 seconds
- Single test: <2 seconds

**Bottlenecks:**
- Database queries: Mostly I/O bound
- LLM operations: May timeout if Ollama unavailable
- Async operations: Network I/O (reduced in tests with mocking)

## Future Enhancements

### 1. Mock LLM Responses
Currently tests make real calls to Ollama. Consider mocking:
```python
@patch('services.llm.ask_ollama')
def test_memory_query(mock_llm):
    mock_llm.return_value = "Mocked response"
    # Test proceeds...
```

### 2. Fixture Factories
Create factories for complex object graphs:
```python
@pytest.fixture
def user_with_week_of_data(db):
    user = create_user(db)
    create_events(db, user, days=7)
    return user
```

### 3. Report Generation
Generate HTML reports per CI run:
```bash
pytest tests/test_integration.py --html=report.html --self-contained-html
```

### 4. Performance Profiling
Add performance thresholds:
```python
def test_analytics_performance():
    with Timer() as t:
        response = calculate_daily_stats(db, days=30)
    assert t.elapsed < 1.0, "Should calculate stats in <1 second"
```

### 5. Chaos Testing
Simulate failures:
```python
def test_analytics_with_missing_activities(db_with_gaps):
    # Database has orphaned events (activity deleted)
    # Verify system handles gracefully
    result = calculate_daily_stats(db_with_gaps)
    assert result is not None  # Doesn't crash
```

## Quick Reference

**Most Important Tests:**
1. `test_daily_stats_aggregation_pipeline` - Core aggregation
2. `test_streak_detection_pipeline` - Streak logic
3. `test_full_daily_workflow` - End-to-end
4. `test_burnout_alert_generation` - Critical feature

**Quick Test Commands:**
```bash
# Run just the essential tests
pytest tests/test_integration.py::TestAnalyticsPipeline -v
pytest tests/test_integration.py::TestEndToEndPipeline -v

# Run with minimal output
pytest tests/test_integration.py -q

# Stop on first failure
pytest tests/test_integration.py -x
```

---

**Created:** 2024-01-15
**Status:** Ready for testing
**Next Step:** Run tests and address any failures
