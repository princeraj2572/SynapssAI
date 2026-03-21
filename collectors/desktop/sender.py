import requests
import logging
import os

logger = logging.getLogger(__name__)

API_URL = os.environ.get("LIFE_OS_API", "http://localhost:8080")


def send_batch(events: list):
    if not events:
        return
    try:
        resp = requests.post(
            f"{API_URL}/api/track/batch",
            json={"events": events},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"Batch sent: {data.get('count', 0)} events")
    except requests.ConnectionError:
        logger.warning("API not reachable. Events will be retried next cycle.")
    except Exception as e:
        logger.error(f"Batch send failed: {e}")


def send_single(event: dict):
    try:
        resp = requests.post(f"{API_URL}/api/track", json=event, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Single send failed: {e}")
