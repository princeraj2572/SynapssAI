"""
Git Scanner — finds all local Git repos and logs new commits to the API.
Run manually or via Task Scheduler every hour.

Usage:
    python scanner.py
    python scanner.py --root C:\\Users\\princ\\projects
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

API_URL     = os.environ.get("LIFE_OS_API", "http://localhost:8080")
STATE_FILE  = Path(__file__).parent / ".last_scan.json"
DEFAULT_ROOTS = [
    str(Path.home() / "projects"),
    str(Path.home() / "Documents"),
    str(Path.home() / "Desktop"),
    "C:\\Users\\princ\\projects",
]


def find_git_repos(root_dirs: list) -> list:
    repos = []
    for root in root_dirs:
        if not os.path.exists(root):
            continue
        for dirpath, dirnames, _ in os.walk(root):
            if ".git" in dirnames:
                repos.append(dirpath)
                dirnames.clear()   # don't recurse into nested repos
    return repos


def get_last_scan_time(repo_path: str) -> datetime:
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
        ts = state.get(repo_path)
        if ts:
            return datetime.fromisoformat(ts)
    return datetime.now(timezone.utc) - timedelta(hours=24)


def save_scan_time(repo_path: str):
    state = {}
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    state[repo_path] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))


def scan_repo(repo_path: str) -> list:
    """Return list of commits since last scan."""
    import subprocess
    since = get_last_scan_time(repo_path)
    since_str = since.strftime("%Y-%m-%d %H:%M:%S")
    repo_name = os.path.basename(repo_path)

    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log",
             f"--since={since_str}",
             "--format=%H|%ai|%s|%an",
             "--shortstat"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return []

        commits = []
        lines = [l for l in result.stdout.strip().split("\n") if l]
        i = 0
        while i < len(lines):
            line = lines[i]
            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 3:
                    commits.append({
                        "activity": "git_commits",
                        "value": 1,
                        "start": parts[1].strip(),
                        "source": "git_scanner",
                        "notes": f"{repo_name}: {parts[2].strip()[:80]}",
                    })
            i += 1

        return commits
    except FileNotFoundError:
        logger.warning("git not found in PATH")
        return []
    except Exception as e:
        logger.error(f"Scan failed for {repo_path}: {e}")
        return []


def send_commits(commits: list):
    if not commits:
        return
    try:
        resp = requests.post(
            f"{API_URL}/api/track/batch",
            json={"events": commits},
            timeout=10,
        )
        resp.raise_for_status()
        logger.info(f"Sent {len(commits)} commits to API")
    except Exception as e:
        logger.error(f"Failed to send commits: {e}")


def run(root_dirs: list = None):
    roots = root_dirs or DEFAULT_ROOTS
    repos = find_git_repos(roots)
    logger.info(f"Found {len(repos)} Git repositories")

    all_commits = []
    for repo in repos:
        commits = scan_repo(repo)
        all_commits.extend(commits)
        if commits:
            logger.info(f"  {os.path.basename(repo)}: {len(commits)} new commits")
        save_scan_time(repo)

    send_commits(all_commits)
    logger.info(f"Git scan complete. Total commits logged: {len(all_commits)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", nargs="+", help="Root directories to scan")
    args = parser.parse_args()
    run(args.root)
