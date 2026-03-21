"""
Generates daily memory sentences from yesterday's data.
Runs nightly at 03:00.
"""
import logging
from datetime import date, timedelta
from db.session import SessionLocal
from services.memory import generate_daily_memory, store_memory
from models.memory import Memory

logger = logging.getLogger(__name__)


def run():
    db = SessionLocal()
    try:
        yesterday = date.today() - timedelta(days=1)

        # Skip if already generated for yesterday
        existing = db.query(Memory).filter(
            Memory.content.like(f"%{yesterday}%"),
            Memory.type == "daily_summary"
        ).first()
        if existing:
            logger.info(f"Memory for {yesterday} already exists, skipping.")
            return

        memory_text = generate_daily_memory(db, yesterday)
        if memory_text:
            store_memory(db, memory_text, "daily_summary")
            logger.info(f"Memory stored for {yesterday}: {memory_text[:80]}...")
        else:
            logger.info(f"No data for {yesterday}, no memory generated.")
    except Exception as e:
        logger.error(f"job_memory failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
