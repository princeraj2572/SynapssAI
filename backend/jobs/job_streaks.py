"""
Updates all streak values. Runs nightly at 00:15.
"""
import logging
from db.session import SessionLocal
from services.streaks import update_all_streaks

logger = logging.getLogger(__name__)


def run():
    db = SessionLocal()
    try:
        update_all_streaks(db)
        logger.info("Streaks updated successfully.")
    except Exception as e:
        logger.error(f"job_streaks failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
