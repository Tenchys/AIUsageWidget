# core/ai_usage_widget/providers/openai.py

import os
import urllib.request
import json
import time


def get_usage(admin_key: str | None = None) -> dict:
    if admin_key is None:
        admin_key = os.environ.get("OPENAI_ADMIN_KEY", "")

    if not admin_key:
        return {
            "provider": "openai",
            "error": "OPENAI_ADMIN_KEY no configurada. Usa: ai-usage config --openai-admin-key KEY",
        }

    now = int(time.time())
    day_ago = now - 86400
    week_ago = now - 7 * 86400
    month_ago = now - 30 * 86400

    cost_today = _fetch_costs(admin_key, day_ago)
    cost_week = _fetch_costs(admin_key, week_ago)
    cost_month = _fetch_costs(admin_key, month_ago)

    return {
        "provider": "openai",
        "cost_today": cost_today,
        "cost_week": cost_week,
        "cost_month": cost_month,
    }


def _fetch_costs(admin_key: str, start_time: int) -> float:
    url = f"https://api.openai.com/v1/organization/costs?start_time={start_time}&limit=1"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {admin_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            total = 0.0
            for bucket in data.get("data", []):
                for result in bucket.get("results", []):
                    total += result.get("amount", {}).get("value", 0) / 100.0
            return round(total, 4)
    except Exception as e:
        return -1.0
