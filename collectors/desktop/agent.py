"""
Desktop Agent — tracks active window every 10 seconds.
Runs as a background daemon on Windows/macOS/Linux.

Usage:
    python agent.py

Requirements:
    pip install pywin32 pynput requests pyyaml   (Windows)
    pip install pyobjc pynput requests pyyaml    (macOS)
    pip install xdotool pynput requests pyyaml   (Linux)
"""
import time
import logging
import platform
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from sender import send_batch
from categorizer import categorize_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Config
POLL_INTERVAL    = 10       # seconds between window polls
IDLE_THRESHOLD   = 180      # seconds of inactivity = idle
BATCH_INTERVAL   = 60       # seconds between API sends
MIN_SESSION_SECS = 30       # ignore sessions shorter than this

OS = platform.system()


def get_active_window() -> str:
    """Return the current active window title."""
    try:
        if OS == "Windows":
            import win32gui
            return win32gui.GetWindowText(win32gui.GetForegroundWindow()) or "Unknown"
        elif OS == "Darwin":
            from AppKit import NSWorkspace
            app = NSWorkspace.sharedWorkspace().activeApplication()
            return app.get("NSApplicationName", "Unknown")
        else:
            import subprocess
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowname"],
                capture_output=True, text=True, timeout=2
            )
            return result.stdout.strip() or "Unknown"
    except Exception as e:
        logger.debug(f"Window fetch failed: {e}")
        return "Unknown"


def is_idle(idle_tracker) -> bool:
    """Returns True if user has been inactive for IDLE_THRESHOLD seconds."""
    return idle_tracker.idle_seconds() >= IDLE_THRESHOLD


class IdleTracker:
    def __init__(self):
        self._last_input = time.time()
        try:
            from pynput import mouse, keyboard
            mouse.Listener(on_move=self._reset, on_click=self._reset, on_scroll=self._reset).start()
            keyboard.Listener(on_press=self._reset).start()
        except Exception as e:
            logger.warning(f"pynput not available, idle detection disabled: {e}")

    def _reset(self, *args, **kwargs):
        self._last_input = time.time()

    def idle_seconds(self) -> float:
        return time.time() - self._last_input


def run():
    logger.info(f"Desktop agent started on {OS}")
    idle_tracker = IdleTracker()
    session_start  = datetime.now(timezone.utc)
    current_window = get_active_window()
    current_app    = _extract_app_name(current_window)
    batch_buffer   = []
    last_batch_send = time.time()

    while True:
        time.sleep(POLL_INTERVAL)

        if is_idle(idle_tracker):
            # Close the current session as idle break
            if current_window != "IDLE":
                _close_session(batch_buffer, current_app, current_window, session_start)
                current_window = "IDLE"
                current_app    = "idle"
            continue

        new_window = get_active_window()
        new_app    = _extract_app_name(new_window)

        if new_window != current_window:
            _close_session(batch_buffer, current_app, current_window, session_start)
            session_start  = datetime.now(timezone.utc)
            current_window = new_window
            current_app    = new_app

        # Send batch every BATCH_INTERVAL seconds
        if time.time() - last_batch_send >= BATCH_INTERVAL and batch_buffer:
            send_batch(batch_buffer)
            batch_buffer.clear()
            last_batch_send = time.time()


def _close_session(buffer, app_name, window_title, start_time):
    end_time = datetime.now(timezone.utc)
    duration_secs = (end_time - start_time).total_seconds()

    if duration_secs < MIN_SESSION_SECS or app_name in ("idle", "Unknown", ""):
        return

    category = categorize_app(app_name)
    hours    = round(duration_secs / 3600, 4)

    # Map category to activity name
    activity = _category_to_activity(category, app_name)

    buffer.append({
        "activity": activity,
        "value": hours,
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "source": "desktop_agent",
        "notes": f"{app_name}: {window_title[:80]}",
    })
    logger.debug(f"Session closed: {app_name} ({category}) for {round(duration_secs)}s")


def _extract_app_name(window_title: str) -> str:
    """Extract short app name from window title."""
    if not window_title:
        return "Unknown"
    # On Windows the title is often "file.py - Visual Studio Code"
    if " - " in window_title:
        return window_title.split(" - ")[-1].strip()
    return window_title.split()[0] if window_title.split() else window_title


def _category_to_activity(category: str, app_name: str) -> str:
    mapping = {
        "coding":        "coding_auto",
        "browser":       "browser_time",
        "communication": "communication",
        "productivity":  "productivity",
        "entertainment": "entertainment",
    }
    return mapping.get(category, "desktop_other")


if __name__ == "__main__":
    run()
