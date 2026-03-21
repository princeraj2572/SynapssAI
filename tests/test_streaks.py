import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from db.session import Base
from models.activity import Activity
from models.daily_stat import DailyStat
from models.streak import Streak
from services.streaks import update_streak, get_all_streaks


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Create test activity
    activity = Activity(id=1, name="coding", category="productivity", unit="hours")
    session.add(activity)
    session.commit()
    yield session
    session.close()


def add_stat(db, activity_id, target_date, value):
    stat = DailyStat(date=target_date, activity_id=activity_id, total_value=value, event_count=1)
    db.add(stat)
    db.commit()


def test_streak_starts_at_one_after_first_day(db):
    add_stat(db, 1, date.today(), 3.0)
    update_streak(db, 1)
    streak = db.query(Streak).filter(Streak.activity_id == 1).first()
    assert streak.current_streak == 1


def test_streak_increments_on_consecutive_days(db):
    today = date.today()
    yesterday = today - timedelta(days=1)
    add_stat(db, 1, yesterday, 2.0)
    # Manually set streak to 1 for yesterday
    s = Streak(activity_id=1, current_streak=1, longest_streak=1, last_date=yesterday)
    db.add(s)
    db.commit()

    add_stat(db, 1, today, 3.0)
    update_streak(db, 1)
    streak = db.query(Streak).filter(Streak.activity_id == 1).first()
    assert streak.current_streak == 2


def test_streak_resets_after_gap(db):
    two_days_ago = date.today() - timedelta(days=2)
    s = Streak(activity_id=1, current_streak=5, longest_streak=5, last_date=two_days_ago)
    db.add(s)
    db.commit()
    # No stat for today or yesterday
    update_streak(db, 1)
    streak = db.query(Streak).filter(Streak.activity_id == 1).first()
    assert streak.current_streak == 0


def test_longest_streak_preserved(db):
    today = date.today()
    yesterday = today - timedelta(days=1)
    s = Streak(activity_id=1, current_streak=9, longest_streak=9, last_date=yesterday)
    db.add(s)
    db.commit()
    add_stat(db, 1, today, 4.0)
    update_streak(db, 1)
    streak = db.query(Streak).filter(Streak.activity_id == 1).first()
    assert streak.current_streak == 10
    assert streak.longest_streak == 10
