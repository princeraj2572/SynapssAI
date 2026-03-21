from sqlalchemy.orm import Session
from datetime import date, timedelta
from models.daily_stat import DailyStat
from models.activity import Activity
from models.alert import Alert


def check_burnout(db: Session) -> list:
    alerts = []
    today = date.today()
    window = [today - timedelta(days=i) for i in range(5)]

    coding_activity = db.query(Activity).filter(Activity.name.ilike("%coding%")).first()
    sleep_activity  = db.query(Activity).filter(Activity.name.ilike("%sleep%")).first()

    if not coding_activity or not sleep_activity:
        return alerts

    high_coding_days = 0
    low_sleep_days = 0

    for d in window:
        cs = db.query(DailyStat).filter(
            DailyStat.activity_id == coding_activity.id,
            DailyStat.date == d
        ).first()
        ss = db.query(DailyStat).filter(
            DailyStat.activity_id == sleep_activity.id,
            DailyStat.date == d
        ).first()

        if cs and cs.total_value > 8:
            high_coding_days += 1
        if ss and ss.total_value < 6:
            low_sleep_days += 1

    if high_coding_days >= 3 and low_sleep_days >= 3:
        existing = db.query(Alert).filter(
            Alert.type == "burnout",
            Alert.dismissed == False
        ).first()
        if not existing:
            alert = Alert(
                type="burnout",
                message=f"Burnout risk detected: {high_coding_days} days of 8+ hour coding sessions with under 6 hours of sleep. Consider taking a break.",
            )
            db.add(alert)
            db.commit()
            alerts.append({"type": "burnout", "message": alert.message})

    return alerts


def get_active_alerts(db: Session) -> list:
    alerts = db.query(Alert).filter(Alert.dismissed == False).order_by(Alert.triggered_at.desc()).all()
    return [
        {
            "id": a.id,
            "type": a.type,
            "message": a.message,
            "triggered_at": str(a.triggered_at),
        }
        for a in alerts
    ]


def dismiss_alert(db: Session, alert_id: int):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.dismissed = True
        db.commit()
