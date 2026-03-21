"""
Background job scheduler for nightly analytics.
Uses APScheduler to run periodic tasks:
- Daily analytics refresh (scoring, streaks, correlations)
- Burnout detection
- Weekly digest generation
"""
import logging
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from models.daily_stat import DailyStat
from models.streak import Streak
from models.activity import Activity
from models.alert import Alert
from models.event import Event
from services.memory import generate_daily_memory, store_memory
from services.llm import generate_weekly_digest
import json

logger = logging.getLogger(__name__)

scheduler = None


def get_db():
    """Get database session."""
    return SessionLocal()


def calculate_daily_stats(db: Session, target_date: date = None):
    """Calculate daily stats (total time per activity) for a given date."""
    if target_date is None:
        target_date = date.today()
    
    logger.info(f"Calculating daily stats for {target_date}")
    
    try:
        # Get all events for the day
        events = (
            db.query(Event)
            .filter(Event.created_at >= datetime.combine(target_date, datetime.min.time()),
                   Event.created_at <= datetime.combine(target_date, datetime.max.time()))
            .all()
        )
        
        # Group by activity and sum values
        activity_totals = {}
        for event in events:
            if event.activity_id not in activity_totals:
                activity_totals[event.activity_id] = 0
            activity_totals[event.activity_id] += event.value
        
        # Store or update daily stats
        for activity_id, total_value in activity_totals.items():
            stat = (
                db.query(DailyStat)
                .filter_by(activity_id=activity_id, date=target_date)
                .first()
            )
            if stat:
                stat.total_value = total_value
            else:
                stat = DailyStat(activity_id=activity_id, date=target_date, total_value=total_value)
                db.add(stat)
        
        db.commit()
        logger.info(f"Daily stats calculated: {len(activity_totals)} activities")
    except Exception as e:
        logger.error(f"Error calculating daily stats: {e}")
        db.rollback()


def detect_streaks(db: Session, target_date: date = None):
    """Detect and update activity streaks."""
    if target_date is None:
        target_date = date.today()
    
    logger.info(f"Detecting streaks as of {target_date}")
    
    try:
        activities = db.query(Activity).all()
        
        for activity in activities:
            # Find if activity was done today
            today_stat = (
                db.query(DailyStat)
                .filter_by(activity_id=activity.id, date=target_date)
                .first()
            )
            
            if not today_stat or today_stat.total_value == 0:
                continue  # Activity not done today, streak broken
            
            # Check existing streak
            streak = (
                db.query(Streak)
                .filter_by(activity_id=activity.id)
                .filter(Streak.end_date.isnull())  # Active (not ended)
                .first()
            )
            
            if streak:
                # Check if streak continues (must have done activity yesterday)
                yesterday = target_date - timedelta(days=1)
                yesterday_stat = (
                    db.query(DailyStat)
                    .filter_by(activity_id=activity.id, date=yesterday)
                    .first()
                )
                
                if yesterday_stat and yesterday_stat.total_value > 0:
                    # Continue streak
                    streak.current_count += 1
                    streak.longest_count = max(streak.longest_count, streak.current_count)
                else:
                    # Streak broken, end it
                    streak.end_date = yesterday
            else:
                # Start new streak
                streak = Streak(
                    activity_id=activity.id,
                    start_date=target_date,
                    current_count=1,
                    longest_count=1,
                )
                db.add(streak)
        
        db.commit()
        logger.info(f"Streaks updated for {len(activities)} activities")
    except Exception as e:
        logger.error(f"Error detecting streaks: {e}")
        db.rollback()


def detect_correlations(db: Session, days: int = 30):
    """Detect correlations between activities (e.g., gym days → higher coding)."""
    logger.info(f"Detecting correlations over last {days} days")
    
    try:
        # Get daily stats for the period
        since = date.today() - timedelta(days=days)
        stats = (
            db.query(DailyStat)
            .filter(DailyStat.date >= since)
            .all()
        )
        
        if not stats:
            logger.info("No stats available for correlation analysis")
            return
        
        # Group by date and activity
        daily_data = {}
        for stat in stats:
            if stat.date not in daily_data:
                daily_data[stat.date] = {}
            daily_data[stat.date][stat.activity_id] = stat.total_value
        
        # Simple correlation: activities that appear on same days increase score
        # This is simplified; real implementation would use statistical correlation
        logger.info(f"Analyzed {len(daily_data)} days of data for patterns")
        
        # TODO: Implement actual correlation matrix and detection
        # For now, log that correlation analysis ran
        
    except Exception as e:
        logger.error(f"Error detecting correlations: {e}")


def detect_burnout(db: Session, threshold_days: int = 7):
    """Detect burnout patterns (high workload + low sleep for consecutive days)."""
    logger.info(f"Checking for burnout patterns in last {threshold_days} days")
    
    try:
        since = date.today() - timedelta(days=threshold_days)
        stats = (
            db.query(DailyStat, Activity)
            .join(Activity, DailyStat.activity_id == Activity.id)
            .filter(DailyStat.date >= since)
            .all()
        )
        
        if not stats:
            logger.info("No stats available for burnout detection")
            return
        
        # Group by date
        daily_activities = {}
        for stat, activity in stats:
            if stat.date not in daily_activities:
                daily_activities[stat.date] = {"coding": 0, "sleep": 0, "exercise": 0}
            
            if activity.name in ["coding", "coding_auto"]:
                daily_activities[stat.date]["coding"] += stat.total_value
            elif activity.name == "sleep":
                daily_activities[stat.date]["sleep"] = stat.total_value
            elif activity.name in ["exercise", "gym", "yoga"]:
                daily_activities[stat.date]["exercise"] += stat.total_value
        
        # Detect burnout: high coding + low sleep for multiple days
        burnout_days = 0
        for day, activities in sorted(daily_activities.items()):
            if activities.get("coding", 0) > 8 and activities.get("sleep", 0) < 6:
                burnout_days += 1
        
        if burnout_days >= threshold_days:
            # Create alert
            alert = Alert(
                type="burnout_warning",
                message=f"High workload with insufficient sleep detected over {threshold_days} days. Consider reducing workload or improving sleep.",
            )
            db.add(alert)
            db.commit()
            logger.warning(f"Burnout alert created: {burnout_days} days of high work + low sleep")
        else:
            logger.info(f"No burnout pattern detected ({burnout_days}/{threshold_days} threshold days)")
        
    except Exception as e:
        logger.error(f"Error detecting burnout: {e}")
        db.rollback()


def generate_weekly_digest_job(db: Session):
    """Generate and store weekly digest."""
    logger.info("Generating weekly digest")
    
    try:
        today = date.today()
        week_start = today - timedelta(days=7)
        
        # Gather week's data
        stats = (
            db.query(DailyStat, Activity)
            .join(Activity, DailyStat.activity_id == Activity.id)
            .filter(DailyStat.date >= week_start, DailyStat.date <= today)
            .all()
        )
        
        week_summary = {}
        for stat, activity in stats:
            if activity.name not in week_summary:
                week_summary[activity.name] = []
            week_summary[activity.name].append({
                "date": str(stat.date),
                "value": stat.total_value,
                "unit": activity.unit,
            })
        
        # Generate digest
        import asyncio
        digest = asyncio.run(generate_weekly_digest(week_summary))
        
        # Store as memory
        store_memory(db, f"Weekly digest ({week_start} to {today}):\n{digest}", memory_type="weekly_digest")
        
        logger.info("Weekly digest generated and stored")
    except Exception as e:
        logger.error(f"Error generating weekly digest: {e}")


def daily_analytics_job():
    """Main job: run all daily analytics tasks."""
    db = get_db()
    try:
        logger.info("=== Daily Analytics Job Starting ===")
        
        # Run all tasks
        calculate_daily_stats(db)
        detect_streaks(db)
        detect_correlations(db)
        detect_burnout(db)
        generate_weekly_digest_job(db)
        
        logger.info("=== Daily Analytics Job Completed ===")
    except Exception as e:
        logger.error(f"Daily analytics job failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler."""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    scheduler = BackgroundScheduler()
    
    # Schedule daily analytics at 11 PM
    scheduler.add_job(
        daily_analytics_job,
        trigger=CronTrigger(hour=23, minute=0),
        id="daily_analytics",
        name="Daily Analytics Job",
        replace_existing=True,
    )
    
    # Also run at startup to catch up
    daily_analytics_job()
    
    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler
    
    if scheduler:
        scheduler.shutdown(wait=True)
        scheduler = None
        logger.info("Background scheduler stopped")


def restart_scheduler():
    """Restart the scheduler."""
    stop_scheduler()
    start_scheduler()


# Initialize scheduler on module load
try:
    start_scheduler()
except Exception as e:
    logger.warning(f"Could not start scheduler: {e}")
