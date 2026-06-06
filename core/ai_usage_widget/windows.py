# core/ai_usage_widget/windows.py

import time
from dataclasses import dataclass
from .pricing.opencode_go import LIMITS, WINDOW_SECONDS


@dataclass
class WindowStatus:
    name: str
    limit: float
    used: float
    remaining: float
    reset_at: float
    percent: float


def get_windows(usage_sessions: list[dict], now: float | None = None, subscription_start: float | None = None) -> list[WindowStatus]:
    if now is None:
        now = time.time()

    windows = []
    for name, seconds in WINDOW_SECONDS.items():
        limit = LIMITS[name]

        if subscription_start:
            elapsed = now - subscription_start
            window_index = int(elapsed // seconds)
            window_start = subscription_start + window_index * seconds
            window_end = window_start + seconds
            cutoff = window_start
        else:
            cutoff = now - seconds

        in_window = [s for s in usage_sessions if s.get("timestamp", 0) >= cutoff]
        used = sum(s.get("cost", 0) for s in in_window)
        remaining = max(0, limit - used)
        percent = (used / limit * 100) if limit > 0 else 0

        if subscription_start:
            reset_at = window_end
        elif in_window:
            oldest_ts = min(s["timestamp"] for s in in_window)
            reset_at = oldest_ts + seconds
        else:
            reset_at = now

        windows.append(WindowStatus(
            name=name,
            limit=limit,
            used=round(used, 2),
            remaining=round(remaining, 2),
            reset_at=reset_at,
            percent=round(min(percent, 100), 1),
        ))

    return windows


def get_reset_time_remaining(reset_at: float, now: float | None = None) -> str:
    if now is None:
        now = time.time()
    remaining = max(0, reset_at - now)
    if remaining <= 0:
        return "ahora"
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def format_reset_time(reset_at: float, now: float | None = None) -> str:
    import datetime
    dt = datetime.datetime.fromtimestamp(reset_at)
    return dt.strftime("%d/%m %H:%M")
