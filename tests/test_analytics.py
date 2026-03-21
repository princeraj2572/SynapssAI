from services.analytics import get_daily_summary
from models.activity import Activity
from models.daily_stat import DailyStat
from datetime import date

def test_daily_summary_returns_stats(db):
    act = Activity(name="coding_test", category="coding", unit="hours")
    db.add(act)
    db.flush()
    today = date.today()
    db.add(DailyStat(date=today, activity_id=act.id, total_value=5.0, event_count=3))
    db.commit()
    result = get_daily_summary(db, today)
    assert result["date"] == str(today)
    assert isinstance(result["stats"], list)
    assert isinstance(result["productivity_score"], (int, float))
