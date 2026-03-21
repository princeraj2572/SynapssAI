from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.streaks import get_all_streaks, update_all_streaks

router = APIRouter(prefix="/api", tags=["streaks"])


@router.get("/streaks")
def streaks(db: Session = Depends(get_db)):
    return {"streaks": get_all_streaks(db)}


@router.post("/streaks/refresh")
def refresh_streaks(db: Session = Depends(get_db)):
    update_all_streaks(db)
    return {"status": "ok", "message": "Streaks updated"}
