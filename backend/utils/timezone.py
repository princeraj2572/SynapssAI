from datetime import datetime, date
import pytz
from config import settings


def now_local() -> datetime:
    tz = pytz.timezone(settings.USER_TIMEZONE)
    return datetime.now(tz)


def today_local() -> date:
    return now_local().date()


def to_local(dt: datetime) -> datetime:
    tz = pytz.timezone(settings.USER_TIMEZONE)
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(tz)
