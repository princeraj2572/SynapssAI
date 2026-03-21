"""
APScheduler setup — registers all nightly background jobs.
Runs inside the FastAPI process automatically on startup.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def start_scheduler():
    from jobs.job_daily_stats  import run as run_daily_stats
    from jobs.job_streaks      import run as run_streaks
    from jobs.job_correlations import run as run_correlations
    from jobs.job_burnout      import run as run_burnout
    from jobs.job_memory       import run as run_memory

    # Midnight: aggregate daily stats
    scheduler.add_job(run_daily_stats,  CronTrigger(hour=0,  minute=5),  id="daily_stats",   replace_existing=True)
    # 00:15: update streaks (after daily stats)
    scheduler.add_job(run_streaks,      CronTrigger(hour=0,  minute=15), id="streaks",        replace_existing=True)
    # 02:00: compute correlations
    scheduler.add_job(run_correlations, CronTrigger(hour=2,  minute=0),  id="correlations",   replace_existing=True)
    # 03:00: generate AI memories
    scheduler.add_job(run_memory,       CronTrigger(hour=3,  minute=0),  id="memory",         replace_existing=True)
    # 06:00: burnout detection
    scheduler.add_job(run_burnout,      CronTrigger(hour=6,  minute=0),  id="burnout",        replace_existing=True)

    scheduler.start()
    logger.info("Scheduler started — nightly jobs registered.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
