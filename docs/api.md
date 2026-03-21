# API Reference

Base URL: `http://localhost:8080`

## Endpoints

### POST /api/track
Ingest a single event.

**Body:**
```json
{
  "activity": "coding",
  "start": "2026-03-18T10:00:00Z",
  "end":   "2026-03-18T12:30:00Z",
  "value": 2.5,
  "source": "desktop"
}
```

### POST /api/track/batch
Ingest multiple events.

### GET /api/analytics/daily?target_date=2026-03-18
Daily summary.

### GET /api/streaks
All current streaks.

### POST /api/memory/query
Ask the AI coach a question.

### GET /health
Service health check.
