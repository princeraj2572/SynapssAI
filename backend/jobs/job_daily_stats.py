"""
Aggregates raw events into daily_stats table.
Runs nightly at 00:05.
"""
import logging
from datetime import date, timedelta
from sqlalchemy import func, cast, Date as SADate
from db.session import SessionLocal
from models.event import Event
from models.activity import Activity
from models.daily_stat import DailyStat

logger = logging.getLogger(__name__)


def run():
    db = SessionLocal()
    try:
        today = date.today()
        yesterday = today - timedelta(days=1)
        _aggregate_for_date(db, yesterday)
        _aggregate_for_date(db, today)
        logger.info(f"Daily stats aggregated for {yesterday} and {today}")
    except Exception as e:
        logger.error(f"job_daily_stats failed: {e}")
    finally:
        db.close()


def _aggregate_for_date(db, target_date: date):
    rows = (
        db.query(Event.activity_id, func.sum(Event.value), func.count(Event.id))
        .filter(cast(Event.start_time, SADate) == target_date)
        .group_by(Event.activity_id)
        .all()
    )
    for activity_id, total_value, event_count in rows:
        existing = db.query(DailyStat).filter(
            DailyStat.date == target_date,
            DailyStat.activity_id == activity_id
        ).first()
        if existing:
            existing.total_value = round(float(total_value or 0), 4)
            existing.event_count = event_count
        else:
            stat = DailyStat(
                date=target_date,
                activity_id=activity_id,
                total_value=round(float(total_value or 0), 4),
                event_count=event_count,
            )
            db.add(stat)
    db.commit()


if __name__ == "__main__":
    run()
