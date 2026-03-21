"""
Computes pairwise Pearson correlations across all activities.
Runs nightly at 02:00.
"""
import logging
from db.session import SessionLocal
from services.analytics import get_correlations

logger = logging.getLogger(__name__)


def run():
    db = SessionLocal()
    try:
        correlations = get_correlations(db)
        logger.info(f"Correlations computed: {len(correlations)} pairs found.")
    except Exception as e:
        logger.error(f"job_correlations failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
