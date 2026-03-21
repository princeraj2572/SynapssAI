"""
Manual Logger CLI — quickly log any activity from the command line.

Usage:
    python cli.py mood 4
    python cli.py sleep 7.5
    python cli.py gym 1 "leg day"
    python cli.py meal lunch "chicken and rice"
    python cli.py coding 3.5 "worked on auth feature"
    python cli.py water 6
    python cli.py custom meditation 20 "20 min morning session"
"""
import sys
import os
import requests
from datetime import datetime, timezone

API_URL = os.environ.get("LIFE_OS_API", "http://localhost:8080")


ALIASES = {
    "c":  "coding", "code": "coding",
    "s":  "study",
    "sl": "sleep",
    "g":  "gym",
    "r":  "run",
    "m":  "mood",
    "e":  "energy",
    "w":  "water",
    "j":  "journal",
}


def send(activity, value, notes=None):
    payload = {
        "activity": activity,
        "value": float(value),
        "start": datetime.now(timezone.utc).isoformat(),
        "source": "manual_cli",
        "notes": notes,
    }
    try:
        resp = requests.post(f"{API_URL}/api/track", json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        print(f"Logged: {activity} = {value}  (id: {data.get('id')})")
    except requests.ConnectionError:
        print("ERROR: API not reachable. Is the server running?")
        print(f"  Start with: cd backend && uvicorn main:app --port 8080")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    activity = ALIASES.get(args[0], args[0])
    value    = float(args[1]) if len(args) > 1 else 1.0
    notes    = " ".join(args[2:]) if len(args) > 2 else None

    send(activity, value, notes)


if __name__ == "__main__":
    main()
