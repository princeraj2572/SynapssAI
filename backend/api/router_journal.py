from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from db.session import get_db
from models.journal import JournalEntry
from schemas.memory import JournalCreateRequest

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.post("")
def create_entry(req: JournalCreateRequest, db: Session = Depends(get_db)):
    d = date.fromisoformat(req.date)
    existing = db.query(JournalEntry).filter(JournalEntry.date == d).first()
    if existing:
        existing.content = req.content
        existing.mood_score = req.mood_score
        db.commit()
        return {"status": "updated", "id": existing.id}
    entry = JournalEntry(date=d, content=req.content, mood_score=req.mood_score)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"status": "created", "id": entry.id}


@router.get("/{entry_date}")
def get_entry(entry_date: str, db: Session = Depends(get_db)):
    d = date.fromisoformat(entry_date)
    entry = db.query(JournalEntry).filter(JournalEntry.date == d).first()
    if not entry:
        raise HTTPException(status_code=404, detail="No journal entry for this date")
    return {"date": str(entry.date), "content": entry.content, "mood_score": entry.mood_score}


@router.get("")
def list_entries(db: Session = Depends(get_db)):
    entries = db.query(JournalEntry).order_by(JournalEntry.date.desc()).limit(30).all()
    return [{"date": str(e.date), "mood_score": e.mood_score, "preview": e.content[:100]} for e in entries]
