from sqlalchemy.orm import Session
from datetime import datetime, timezone
from models.activity import Activity
from models.event import Event
from schemas.track import TrackRequest


def get_or_create_activity(db: Session, name: str) -> Activity:
    activity = db.query(Activity).filter(Activity.name == name).first()
    if not activity:
        activity = Activity(
            name=name,
            category=_guess_category(name),
            unit=_guess_unit(name),
            is_auto=False,
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
    return activity


def ingest_event(db: Session, req: TrackRequest) -> Event:
    activity = get_or_create_activity(db, req.activity)
    event = Event(
        activity_id=activity.id,
        start_time=req.start or datetime.now(timezone.utc),
        end_time=req.end,
        value=req.value if req.value is not None else 1.0,
        source=req.source or "manual",
        notes=req.notes,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def ingest_batch(db: Session, events: list) -> list:
    results = []
    for req in events:
        event = ingest_event(db, req)
        results.append(event)
    return results


def _guess_category(name: str) -> str:
    name_lower = name.lower()
    mapping = {
        "coding": "productivity", "study": "productivity", "reading": "productivity",
        "leetcode": "productivity", "writing": "productivity",
        "gym": "health", "run": "health", "workout": "health", "sleep": "health",
        "walk": "health", "yoga": "health", "meditation": "health",
        "meal": "nutrition", "breakfast": "nutrition", "lunch": "nutrition",
        "dinner": "nutrition", "water": "nutrition",
        "mood": "mental", "journal": "mental", "stress": "mental",
        "phone": "screen", "social_media": "screen",
    }
    for key, cat in mapping.items():
        if key in name_lower:
            return cat
    return "general"


def _guess_unit(name: str) -> str:
    name_lower = name.lower()
    if any(k in name_lower for k in ["coding", "study", "sleep", "reading", "workout", "gym"]):
        return "hours"
    if any(k in name_lower for k in ["steps", "pages"]):
        return "count"
    if "mood" in name_lower or "score" in name_lower:
        return "score"
    return "count"
