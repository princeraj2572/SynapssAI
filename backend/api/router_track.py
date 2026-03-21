from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.track import TrackRequest, BatchTrackRequest
from services.ingestion import ingest_event, ingest_batch

router = APIRouter(prefix="/api", tags=["tracking"])


@router.post("/track")
def track_event(req: TrackRequest, db: Session = Depends(get_db)):
    event = ingest_event(db, req)
    return {"status": "ok", "activity": req.activity, "id": event.id}


@router.post("/track/batch")
def track_batch(req: BatchTrackRequest, db: Session = Depends(get_db)):
    events = ingest_batch(db, req.events)
    return {"status": "ok", "count": len(events), "ids": [e.id for e in events]}
