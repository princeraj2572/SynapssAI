from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from db.session import get_db
from services.analytics import get_daily_summary, get_weekly_summary, get_history, get_correlations
from services.scoring import compute_today_score

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/daily")
def daily(target_date: str = Query(default=None), db: Session = Depends(get_db)):
    d = date.fromisoformat(target_date) if target_date else date.today()
    return get_daily_summary(db, d)


@router.get("/weekly")
def weekly(week_start: str = Query(default=None), db: Session = Depends(get_db)):
    if week_start:
        ws = date.fromisoformat(week_start)
    else:
        today = date.today()
        ws = today - timedelta(days=today.weekday())
    return get_weekly_summary(db, ws)


@router.get("/history/{activity_name}")
def history(activity_name: str, days: int = Query(default=30), db: Session = Depends(get_db)):
    return {"activity": activity_name, "data": get_history(db, activity_name, days)}


@router.get("/correlations")
def correlations(db: Session = Depends(get_db)):
    return {"correlations": get_correlations(db)}


@router.get("/score")
def score(db: Session = Depends(get_db)):
    return compute_today_score(db)
