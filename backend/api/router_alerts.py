from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.burnout import get_active_alerts, dismiss_alert, check_burnout

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def alerts(db: Session = Depends(get_db)):
    return {"alerts": get_active_alerts(db)}


@router.post("/check")
def run_burnout_check(db: Session = Depends(get_db)):
    new_alerts = check_burnout(db)
    return {"status": "ok", "new_alerts": new_alerts}


@router.post("/{alert_id}/dismiss")
def dismiss(alert_id: int, db: Session = Depends(get_db)):
    dismiss_alert(db, alert_id)
    return {"status": "ok"}
