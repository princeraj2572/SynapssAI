import pytest

@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_track_stub(client):
    payload = {
        "activity": "coding",
        "start": "2026-03-18T10:00:00Z",
        "end":   "2026-03-18T12:00:00Z",
        "value": 2.0,
        "source": "test"
    }
    r = await client.post("/api/track", json=payload)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_burnout_logic():
    from services.burnout import check_burnout
    days = [
        {"date": "2026-03-15", "coding_hours": 11, "sleep_hours": 5},
        {"date": "2026-03-16", "coding_hours": 12, "sleep_hours": 5},
        {"date": "2026-03-17", "coding_hours": 11, "sleep_hours": 4},
    ]
    warnings = check_burnout(days)
    assert len(warnings) > 0

@pytest.mark.asyncio
async def test_scoring_logic():
    from services.scoring import compute_score
    score = compute_score({"coding": 8, "study": 3, "gym": 1, "sleep": 7})
    assert score == 100.0
    score_low = compute_score({"coding": 0, "study": 0, "gym": 0, "sleep": 0})
    assert score_low == 0.0
