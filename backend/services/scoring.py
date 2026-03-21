from sqlalchemy.orm import Session
from datetime import date
from models.daily_stat import DailyStat
from models.activity import Activity


def compute_today_score(db: Session) -> dict:
    today = date.today()
    stats = (
        db.query(DailyStat, Activity)
        .join(Activity, DailyStat.activity_id == Activity.id)
        .filter(DailyStat.date == today)
        .all()
    )

    coding_hours = 0.0
    study_hours = 0.0
    sleep_hours = 0.0
    gym_done = False
    phone_hours = 0.0

    for stat, activity in stats:
        n = activity.name.lower()
        if "coding" in n:
            coding_hours += stat.total_value
        if "study" in n:
            study_hours += stat.total_value
        if "sleep" in n:
            sleep_hours += stat.total_value
        if "gym" in n or "workout" in n:
            gym_done = stat.total_value > 0
        if "phone" in n or "screen" in n:
            phone_hours += stat.total_value

    coding_score  = min(coding_hours / 6.0, 1.0) * 35
    study_score   = min(study_hours / 3.0, 1.0) * 25
    sleep_score   = min(sleep_hours / 7.0, 1.0) * 25
    gym_score     = 15.0 if gym_done else 0.0
    phone_penalty = min(phone_hours / 4.0, 1.0) * 10

    total = max(0, coding_score + study_score + sleep_score + gym_score - phone_penalty)

    return {
        "score": round(total, 1),
        "breakdown": {
            "coding": round(coding_score, 1),
            "study": round(study_score, 1),
            "sleep": round(sleep_score, 1),
            "gym": round(gym_score, 1),
            "phone_penalty": round(-phone_penalty, 1),
        },
        "inputs": {
            "coding_hours": round(coding_hours, 2),
            "study_hours": round(study_hours, 2),
            "sleep_hours": round(sleep_hours, 2),
            "gym_done": gym_done,
            "phone_hours": round(phone_hours, 2),
        }
    }
