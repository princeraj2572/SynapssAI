"""
Seed default activities into the database.
Run: python scripts/seed_activities.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db.session import SessionLocal
from models.activity import Activity

DEFAULT_ACTIVITIES = [
    # Productivity
    {"name": "coding",       "category": "productivity", "unit": "hours",  "target_value": 6.0,  "description": "Coding / programming sessions"},
    {"name": "study",        "category": "productivity", "unit": "hours",  "target_value": 3.0,  "description": "Studying / reading academic material"},
    {"name": "leetcode",     "category": "productivity", "unit": "count",  "target_value": 2.0,  "description": "LeetCode problems solved"},
    {"name": "reading",      "category": "productivity", "unit": "pages",  "target_value": 20.0, "description": "Book reading (pages)"},
    {"name": "writing",      "category": "productivity", "unit": "hours",  "target_value": 1.0,  "description": "Writing sessions"},

    # Health
    {"name": "sleep",        "category": "health",       "unit": "hours",  "target_value": 7.5,  "description": "Sleep duration"},
    {"name": "gym",          "category": "health",       "unit": "hours",  "target_value": 1.0,  "description": "Gym / weight training"},
    {"name": "run",          "category": "health",       "unit": "km",     "target_value": 5.0,  "description": "Running distance"},
    {"name": "steps",        "category": "health",       "unit": "count",  "target_value": 8000, "description": "Daily step count"},
    {"name": "meditation",   "category": "health",       "unit": "minutes","target_value": 10.0, "description": "Meditation / mindfulness"},

    # Nutrition
    {"name": "meal",         "category": "nutrition",    "unit": "count",  "target_value": 3.0,  "description": "Meals eaten"},
    {"name": "water",        "category": "nutrition",    "unit": "glasses","target_value": 8.0,  "description": "Water intake (glasses)"},
    {"name": "coffee",       "category": "nutrition",    "unit": "cups",   "target_value": 2.0,  "description": "Coffee / caffeine intake"},

    # Mental
    {"name": "mood",         "category": "mental",       "unit": "score",  "target_value": 4.0,  "description": "Mood rating (1-5)"},
    {"name": "energy",       "category": "mental",       "unit": "score",  "target_value": 4.0,  "description": "Energy level (1-5)"},
    {"name": "journal",      "category": "mental",       "unit": "count",  "target_value": 1.0,  "description": "Daily journal entry written"},

    # Screen
    {"name": "phone_usage",  "category": "screen",       "unit": "hours",  "target_value": 2.0,  "description": "Total phone screen time"},
    {"name": "social_media", "category": "screen",       "unit": "hours",  "target_value": 0.5,  "description": "Social media time"},

    # Auto-tracked (set by collectors)
    {"name": "coding_auto",  "category": "productivity", "unit": "hours",  "target_value": 6.0,  "description": "Auto-tracked coding (desktop agent)", "is_auto": True},
    {"name": "browser_time", "category": "screen",       "unit": "hours",  "target_value": 2.0,  "description": "Auto-tracked browser time", "is_auto": True},
    {"name": "git_commits",  "category": "productivity", "unit": "count",  "target_value": 3.0,  "description": "Git commits today", "is_auto": True},
]


def seed():
    db = SessionLocal()
    added = 0
    skipped = 0
    try:
        for data in DEFAULT_ACTIVITIES:
            existing = db.query(Activity).filter(Activity.name == data["name"]).first()
            if existing:
                skipped += 1
                continue
            activity = Activity(**data)
            db.add(activity)
            added += 1
        db.commit()
        print(f"Seeding complete: {added} added, {skipped} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
