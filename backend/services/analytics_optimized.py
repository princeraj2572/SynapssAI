"""
Optimized analytics queries with caching and batch operations.
Includes query profiling and performance monitoring.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from typing import List, Dict
import logging
import time

from models.daily_stat import DailyStat
from models.activity import Activity
from models.event import Event
from models.streak import Streak
from services.cache import get_cache, cached

logger = logging.getLogger(__name__)


def profile_query(func_name: str):
    """Decorator to profile query execution time."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            if elapsed > 0.1:  # Log slow queries (>100ms)
                logger.warning(f"SLOW QUERY: {func_name} took {elapsed:.3f}s")
            else:
                logger.debug(f"QUERY: {func_name} took {elapsed:.3f}s")
            return result
        return wrapper
    return decorator


@profile_query("get_daily_summary")
@cached(ttl=3600, key_prefix="daily_summary")
def get_daily_summary_cached(db: Session, target_date: date) -> dict:
    """
    Get daily summary with caching.
    Uses single query with joins instead of N+1.
    """
    # Single query: join DailyStat with Activity
    results = (
        db.query(DailyStat, Activity)
        .join(Activity, DailyStat.activity_id == Activity.id)
        .filter(DailyStat.date == target_date)
        .all()
    )
    
    # Process results
    activities = []
    coding_hours = 0.0
    sleep_hours = 0.0
    gym_done = False
    
    for stat, activity in results:
        activities.append({
            "activity": activity.name,
            "category": activity.category,
            "total_value": round(stat.total_value, 2),
            "event_count": stat.event_count,
            "unit": activity.unit,
        })
        
        # Accumulate metrics
        if "coding" in activity.name.lower():
            coding_hours += stat.total_value
        if "sleep" in activity.name.lower():
            sleep_hours += stat.total_value
        if "gym" in activity.name.lower() or "workout" in activity.name.lower():
            gym_done = stat.total_value > 0
    
    return {
        "date": str(target_date),
        "activities": activities,
        "total_coding_hours": round(coding_hours, 2),
        "sleep_hours": round(sleep_hours, 2),
        "gym_done": gym_done,
    }


@profile_query("get_weekly_summary")
@cached(ttl=7200, key_prefix="weekly_summary")
def get_weekly_summary_cached(db: Session, week_start: date) -> dict:
    """
    Get weekly summary with caching.
    Aggregates 7 days in single query.
    """
    week_end = week_start + timedelta(days=6)
    
    # Aggregate in database instead of Python
    results = (
        db.query(
            Activity.name,
            Activity.category,
            Activity.unit,
            func.sum(DailyStat.total_value).label('total_value'),
            func.sum(DailyStat.event_count).label('event_count')
        )
        .join(DailyStat, Activity.id == DailyStat.activity_id)
        .filter(and_(DailyStat.date >= week_start, DailyStat.date <= week_end))
        .group_by(Activity.id, Activity.name, Activity.category, Activity.unit)
        .all()
    )
    
    activities = [
        {
            "activity": r.name,
            "total_value": round(float(r.total_value), 2) if r.total_value else 0.0,
            "event_count": r.event_count or 0,
            "category": r.category,
            "unit": r.unit,
        }
        for r in results
    ]
    
    top_activity = max(activities, key=lambda x: x["total_value"])["activity"] if activities else "none"
    
    return {
        "week_start": str(week_start),
        "week_end": str(week_end),
        "activities": activities,
        "top_activity": top_activity,
    }


@profile_query("get_activity_history")
def get_activity_history_cached(db: Session, activity_id: int, days: int = 30) -> list:
    """
    Get activity history for last N days with index optimization.
    Uses (activity_id, date) composite index.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Use indexed query
    stats = (
        db.query(DailyStat)
        .filter(
            DailyStat.activity_id == activity_id,
            DailyStat.date >= start_date
        )
        .order_by(DailyStat.date)
        .all()
    )
    
    return [
        {
            "date": str(s.date),
            "value": round(s.total_value, 2),
            "event_count": s.event_count,
        }
        for s in stats
    ]


@profile_query("get_recent_alerts")
def get_recent_alerts_cached(db: Session, days: int = 7, limit: int = 10) -> list:
    """
    Get recent unread alerts using index.
    Uses (type, dismissed) composite index.
    """
    since = date.today() - timedelta(days=days)
    
    alerts = (
        db.query(Alert)
        .filter(
            Alert.dismissed == False,
            Alert.triggered_at >= since
        )
        .order_by(Alert.triggered_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": a.id,
            "type": a.type,
            "message": a.message,
            "triggered_at": str(a.triggered_at),
        }
        for a in alerts
    ]


@profile_query("get_streaks")
def get_streaks_cached(db: Session) -> list:
    """
    Get all active streaks with activity information.
    Uses eager loading to avoid N+1.
    """
    streaks = (
        db.query(Streak, Activity)
        .join(Activity, Streak.activity_id == Activity.id)
        .filter(Streak.current_count > 0)
        .order_by(Streak.current_count.desc())
        .all()
    )
    
    return [
        {
            "activity": activity.name,
            "current_count": streak.current_count,
            "longest_count": streak.longest_count,
            "start_date": str(streak.start_date),
        }
        for streak, activity in streaks
    ]


def batch_insert_events(db: Session, events_data: List[Dict]) -> int:
    """
    Efficiently insert multiple events using batch operation.
    Faster than individual inserts.
    
    Args:
        db: Database session
        events_data: List of event dictionaries
    
    Returns:
        Number of events inserted
    """
    if not events_data:
        return 0
    
    try:
        event_objects = [Event(**data) for data in events_data]
        db.bulk_insert_mappings(Event, events_data)
        db.commit()
        logger.info(f"Batch inserted {len(events_data)} events")
        return len(events_data)
    except Exception as e:
        logger.error(f"Batch insert error: {e}")
        db.rollback()
        return 0


def batch_update_daily_stats(db: Session, stats_data: List[Dict]) -> int:
    """
    Efficiently update multiple daily stats using merge operation.
    
    Args:
        db: Database session
        stats_data: List of stat dictionaries
    
    Returns:
        Number of stats updated
    """
    if not stats_data:
        return 0
    
    try:
        count = 0
        for stat_dict in stats_data:
            db.merge(DailyStat(**stat_dict))
            count += 1
        db.commit()
        logger.info(f"Batch updated {count} daily stats")
        return count
    except Exception as e:
        logger.error(f"Batch update error: {e}")
        db.rollback()
        return 0


def invalidate_cache_for_date(target_date: date):
    """
    Invalidate cache entries for a specific date.
    Called after daily stats calculation.
    """
    cache = get_cache()
    cache.delete(f"daily_summary:{target_date}")
    
    # Invalidate weekly summary if target_date is in week
    week_start = target_date - timedelta(days=target_date.weekday())
    cache.delete(f"weekly_summary:{week_start}")
    
    logger.info(f"Invalidated cache for {target_date}")


def get_query_performance_stats() -> dict:
    """
    Get performance statistics including cache metrics.
    Useful for debugging and optimization.
    """
    cache = get_cache()
    return {
        "cache": cache.get_stats(),
        "timestamp": time.time(),
    }


# Profiling context manager
class QueryProfiler:
    """Context manager for profiling query sections."""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.elapsed = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        if self.elapsed > 0.1:
            logger.warning(f"SLOW: {self.name} took {self.elapsed:.3f}s")
        else:
            logger.debug(f"PROFILE: {self.name} took {self.elapsed:.3f}s")


# Import Alert model (defined elsewhere)
from models.alert import Alert
