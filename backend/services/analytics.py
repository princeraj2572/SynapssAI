from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date, timedelta
from typing import List, Dict
import pandas as pd
import numpy as np

from models.event import Event
from models.activity import Activity
from models.daily_stat import DailyStat
from models.streak import Streak


def get_daily_summary(db: Session, target_date: date) -> dict:
    stats = (
        db.query(DailyStat, Activity)
        .join(Activity, DailyStat.activity_id == Activity.id)
        .filter(DailyStat.date == target_date)
        .all()
    )

    activities = []
    coding_hours = 0.0
    study_hours = 0.0
    sleep_hours = 0.0
    gym_done = False

    for stat, activity in stats:
        activities.append({
            "activity": activity.name,
            "category": activity.category,
            "total_value": round(stat.total_value, 2),
            "event_count": stat.event_count,
            "unit": activity.unit,
        })
        if "coding" in activity.name.lower():
            coding_hours += stat.total_value
        if "study" in activity.name.lower():
            study_hours += stat.total_value
        if "sleep" in activity.name.lower():
            sleep_hours += stat.total_value
        if "gym" in activity.name.lower() or "workout" in activity.name.lower():
            gym_done = stat.total_value > 0

    score = compute_score(coding_hours, study_hours, sleep_hours, gym_done)

    return {
        "date": str(target_date),
        "activities": activities,
        "productivity_score": score,
        "total_coding_hours": round(coding_hours, 2),
        "total_study_hours": round(study_hours, 2),
        "sleep_hours": round(sleep_hours, 2),
        "gym_done": gym_done,
    }


def get_weekly_summary(db: Session, week_start: date) -> dict:
    week_end = week_start + timedelta(days=6)
    stats = (
        db.query(DailyStat, Activity)
        .join(Activity, DailyStat.activity_id == Activity.id)
        .filter(DailyStat.date >= week_start, DailyStat.date <= week_end)
        .all()
    )

    totals: Dict[str, dict] = {}
    for stat, activity in stats:
        if activity.name not in totals:
            totals[activity.name] = {"total": 0.0, "count": 0, "category": activity.category, "unit": activity.unit}
        totals[activity.name]["total"] += stat.total_value
        totals[activity.name]["count"] += stat.event_count

    activities = [
        {"activity": name, "total_value": round(v["total"], 2), "event_count": v["count"],
         "category": v["category"], "unit": v["unit"]}
        for name, v in totals.items()
    ]

    top = max(activities, key=lambda x: x["total_value"])["activity"] if activities else "none"

    return {
        "week_start": str(week_start),
        "week_end": str(week_end),
        "activities": activities,
        "top_activity": top,
    }


def get_history(db: Session, activity_name: str, days: int = 30) -> list:
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        return []

    stats = (
        db.query(DailyStat)
        .filter(DailyStat.activity_id == activity.id, DailyStat.date >= start_date)
        .order_by(DailyStat.date)
        .all()
    )
    return [{"date": str(s.date), "value": round(s.total_value, 2)} for s in stats]


def get_correlations(db: Session) -> list:
    end_date = date.today()
    start_date = end_date - timedelta(days=60)

    stats = (
        db.query(DailyStat, Activity)
        .join(Activity, DailyStat.activity_id == Activity.id)
        .filter(DailyStat.date >= start_date)
        .all()
    )

    if not stats:
        return []

    rows = {}
    for stat, activity in stats:
        d = str(stat.date)
        if d not in rows:
            rows[d] = {}
        rows[d][activity.name] = stat.total_value

    df = pd.DataFrame.from_dict(rows, orient="index").fillna(0)
    if df.shape[1] < 2:
        return []

    corr = df.corr(method="pearson")
    results = []
    seen = set()
    for col_a in corr.columns:
        for col_b in corr.columns:
            if col_a == col_b:
                continue
            pair = tuple(sorted([col_a, col_b]))
            if pair in seen:
                continue
            seen.add(pair)
            r = corr.loc[col_a, col_b]
            if np.isnan(r):
                continue
            r = round(float(r), 3)
            if abs(r) < 0.2:
                continue
            results.append({
                "activity_a": col_a,
                "activity_b": col_b,
                "correlation": r,
                "interpretation": _interpret_correlation(r),
            })

    return sorted(results, key=lambda x: abs(x["correlation"]), reverse=True)


def compute_score(coding_hours: float, study_hours: float, sleep_hours: float, gym_done: bool) -> float:
    coding_score  = min(coding_hours / 6.0, 1.0) * 35
    study_score   = min(study_hours / 3.0, 1.0) * 25
    sleep_score   = min(sleep_hours / 7.0, 1.0) * 25
    gym_score     = 15.0 if gym_done else 0.0
    return round(coding_score + study_score + sleep_score + gym_score, 1)


def _interpret_correlation(r: float) -> str:
    if r >= 0.7:
        return "strong positive"
    elif r >= 0.4:
        return "moderate positive"
    elif r >= 0.2:
        return "weak positive"
    elif r <= -0.7:
        return "strong negative"
    elif r <= -0.4:
        return "moderate negative"
    else:
        return "weak negative"
