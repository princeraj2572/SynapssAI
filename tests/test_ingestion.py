"""
Tests for the event ingestion service.
Run: cd backend && pytest ../tests/ -v
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from db.session import Base
from models.activity import Activity
from models.event import Event
from services.ingestion import ingest_event, get_or_create_activity, _guess_category
from schemas.track import TrackRequest


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_creates_new_activity_on_first_track(db):
    req = TrackRequest(activity="coding", value=2.5, source="test")
    event = ingest_event(db, req)
    assert event.id is not None
    assert event.value == 2.5
    activity = db.query(Activity).filter(Activity.name == "coding").first()
    assert activity is not None


def test_reuses_existing_activity(db):
    req1 = TrackRequest(activity="gym", value=1.0, source="test")
    req2 = TrackRequest(activity="gym", value=0.5, source="test")
    ingest_event(db, req1)
    ingest_event(db, req2)
    count = db.query(Activity).filter(Activity.name == "gym").count()
    assert count == 1


def test_event_stored_with_correct_values(db):
    now = datetime.now(timezone.utc)
    req = TrackRequest(activity="sleep", value=7.5, start=now, source="manual", notes="good sleep")
    event = ingest_event(db, req)
    assert event.value == 7.5
    assert event.source == "manual"
    assert event.notes == "good sleep"


def test_category_guessing():
    assert _guess_category("coding") == "productivity"
    assert _guess_category("gym") == "health"
    assert _guess_category("sleep") == "health"
    assert _guess_category("meal") == "nutrition"
    assert _guess_category("mood") == "mental"
    assert _guess_category("phone_usage") == "screen"
    assert _guess_category("random_thing") == "general"


def test_default_value_is_one(db):
    req = TrackRequest(activity="journal")
    event = ingest_event(db, req)
    assert event.value == 1.0
