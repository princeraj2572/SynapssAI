"""
Checks burnout rules and creates alerts. Runs at 06:00.
"""
import logging
from db.session import SessionLocal
from services.burnout import check_burnout

logger = logging.getLogger(__name__)


def run():
    db = SessionLocal()
    try:
        alerts = check_burnout(db)
        if alerts:
            logger.warning(f"Burnout alerts created: {len(alerts)}")
        else:
            logger.info("Burnout check passed — no alerts.")
    except Exception as e:
        logger.error(f"job_burnout failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
