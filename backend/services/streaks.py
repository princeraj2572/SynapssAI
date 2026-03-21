from sqlalchemy.orm import Session
from datetime import date, timedelta
from models.streak import Streak
from models.daily_stat import DailyStat
from models.activity import Activity


def update_all_streaks(db: Session):
    activities = db.query(Activity).all()
    for activity in activities:
        update_streak(db, activity.id)


def update_streak(db: Session, activity_id: int):
    today = date.today()
    yesterday = today - timedelta(days=1)

    streak = db.query(Streak).filter(Streak.activity_id == activity_id).first()
    if not streak:
        streak = Streak(activity_id=activity_id, current_streak=0, longest_streak=0)
        db.add(streak)

    has_today = db.query(DailyStat).filter(
        DailyStat.activity_id == activity_id,
        DailyStat.date == today,
        DailyStat.total_value > 0,
    ).first()

    has_yesterday = db.query(DailyStat).filter(
        DailyStat.activity_id == activity_id,
        DailyStat.date == yesterday,
        DailyStat.total_value > 0,
    ).first()

    if has_today:
        if streak.last_date == yesterday or streak.last_date == today:
            if streak.last_date != today:
                streak.current_streak += 1
        else:
            streak.current_streak = 1
        streak.last_date = today
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
    else:
        if streak.last_date and streak.last_date < yesterday:
            streak.current_streak = 0

    db.commit()


def get_all_streaks(db: Session) -> list:
    streaks = (
        db.query(Streak, Activity)
        .join(Activity, Streak.activity_id == Activity.id)
        .all()
    )
    return [
        {
            "activity": activity.name,
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "last_date": str(streak.last_date) if streak.last_date else None,
        }
        for streak, activity in streaks
        if streak.current_streak > 0 or streak.longest_streak > 0
    ]
