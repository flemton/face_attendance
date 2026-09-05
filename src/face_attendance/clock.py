"""Africa/Accra wall clock for every displayed date and time."""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

ACCRA = ZoneInfo("Africa/Accra")

_MONTHS = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


def now() -> datetime:
    return datetime.now(ACCRA)


def today() -> date:
    return now().date()


def today_iso() -> str:
    return today().isoformat()


def format_date(value: date | datetime | str | None = None) -> str:
    """Clerk-facing date, e.g. 4 Sep 2026."""
    d = _as_date(value)
    return f"{d.day} {_MONTHS[d.month - 1]} {d.year}"


def format_time(value: datetime | str | None = None) -> str:
    """24-hour Accra time, e.g. 07:42."""
    if value is None:
        t = now()
        return f"{t.hour:02d}:{t.minute:02d}"
    if isinstance(value, str):
        parts = value.strip().split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        return f"{hour:02d}:{minute:02d}"
    return f"{value.hour:02d}:{value.minute:02d}"


def format_time_long(value: datetime | None = None) -> str:
    t = value or now()
    return f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}"


def _as_date(value: date | datetime | str | None) -> date:
    if value is None:
        return today()
    if isinstance(value, datetime):
        return value.astimezone(ACCRA).date() if value.tzinfo else value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if "T" in text:
        text = text.split("T", 1)[0]
    return date.fromisoformat(text[:10])
