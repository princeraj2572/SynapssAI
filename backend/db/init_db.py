"""
Run once to create all tables and install pgvector extension.
Usage: python db/init_db.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.session import engine, Base
from sqlalchemy import text

# Import all models so Base knows about them
import models.activity
import models.event
import models.daily_stat
import models.streak
import models.memory
import models.journal
import models.goal
import models.alert


def init():
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("pgvector extension enabled.")
        except Exception as e:
            print(f"Warning: pgvector extension not available: {e}")
            print("Continuing without pgvector (semantic search will be limited)")

    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")
    print("\nTables:")
    for table in Base.metadata.tables:
        print(f"  - {table}")


if __name__ == "__main__":
    init()
