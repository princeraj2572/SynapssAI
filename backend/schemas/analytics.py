from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date


class ActivitySummary(BaseModel):
    activity: str
    category: str
    total_value: float
    event_count: int
    unit: str


class DailySummary(BaseModel):
    date: date
    activities: List[ActivitySummary]
    productivity_score: float
    total_coding_hours: float
    total_study_hours: float
    sleep_hours: float
    gym_done: bool


class WeeklySummary(BaseModel):
    week_start: date
    week_end: date
    activities: List[ActivitySummary]
    avg_productivity_score: float
    top_activity: str


class CorrelationResult(BaseModel):
    activity_a: str
    activity_b: str
    correlation: float
    interpretation: str


class StreakInfo(BaseModel):
    activity: str
    current_streak: int
    longest_streak: int
    last_date: Optional[date]
