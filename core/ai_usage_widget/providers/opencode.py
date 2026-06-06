# core/ai_usage_widget/providers/opencode.py

import time
from ..storage import fetch_opencode_sessions
from ..windows import get_windows, WindowStatus
from ..pricing.opencode_go import LIMITS
from ..config import get_subscription_start, set_subscription_start
from scraper.errors import CookieExpiredError


def get_usage() -> dict:
    sessions = fetch_opencode_sessions()

    for s in sessions:
        s["cost"] = s.get("cost", 0) or 0

    go_sessions = [s for s in sessions if s.get("provider") == "opencode-go"]

    source = "local"
    windows = []
    try:
        server_data = _try_scraper()
    except CookieExpiredError as e:
        msg = "Cookie expirada"
        if e.expiry_date:
            msg += f" el {e.expiry_date}"
        msg += ". Ejecutá 'ai-usage setup' para renovarla."
        return {
            "provider": "opencode_go",
            "error": msg,
        }

    if server_data:
        source = "web"
        now = time.time()
        windows = [
            WindowStatus(
                name="5h",
                limit=LIMITS["5h"],
                used=round(server_data.five_hour_pct / 100 * LIMITS["5h"], 2),
                remaining=round(LIMITS["5h"] * (1 - server_data.five_hour_pct / 100), 2),
                reset_at=now + server_data.five_hour_reset_seconds,
                percent=server_data.five_hour_pct,
            ),
            WindowStatus(
                name="weekly",
                limit=LIMITS["weekly"],
                used=round(server_data.weekly_pct / 100 * LIMITS["weekly"], 2),
                remaining=round(LIMITS["weekly"] * (1 - server_data.weekly_pct / 100), 2),
                reset_at=now + server_data.weekly_reset_seconds,
                percent=server_data.weekly_pct,
            ),
            WindowStatus(
                name="monthly",
                limit=LIMITS["monthly"],
                used=round(server_data.monthly_pct / 100 * LIMITS["monthly"], 2),
                remaining=round(LIMITS["monthly"] * (1 - server_data.monthly_pct / 100), 2),
                reset_at=now + server_data.monthly_reset_seconds,
                percent=server_data.monthly_pct,
            ),
        ]
        sub_start = now + server_data.monthly_reset_seconds - 30 * 86400
        set_subscription_start(sub_start)
    else:
        sub_start = get_subscription_start()
        if sub_start:
            windows = get_windows(go_sessions, subscription_start=sub_start)
        else:
            windows = get_windows(go_sessions)

    from scraper.cookies import get_saved_expiry, format_expiry_date
    cookie_expiry = format_expiry_date(get_saved_expiry())

    models_used: dict[str, dict] = {}
    for s in go_sessions:
        model_id = s.get("model_id", "unknown")
        if model_id not in models_used:
            models_used[model_id] = {
                "sessions": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "cost": 0.0,
            }
        models_used[model_id]["sessions"] += 1
        models_used[model_id]["tokens_input"] += s.get("tokens_input", 0)
        models_used[model_id]["tokens_output"] += s.get("tokens_output", 0)
        models_used[model_id]["cost"] += s["cost"]

    return {
        "provider": "opencode_go",
        "total_sessions": len(go_sessions),
        "total_cost": round(sum(s["cost"] for s in go_sessions), 4),
        "windows": windows,
        "models": models_used,
        "source": source,
        "cookie_expiry": cookie_expiry,
    }


def _try_scraper():
    try:
        from scraper.cookies import get_cookies, cookies_to_header, get_saved_expiry, is_expired, format_expiry_date
        from scraper.opencode_go import fetch_go_usage
        from scraper.errors import CookieExpiredError

        expiry = get_saved_expiry()
        if is_expired(expiry):
            raise CookieExpiredError(format_expiry_date(expiry))

        cookies = get_cookies()
        if not cookies:
            return None

        header = cookies_to_header(cookies)
        return fetch_go_usage(header)
    except CookieExpiredError:
        raise
    except Exception:
        return None
