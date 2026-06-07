# core/ai_usage_widget/storage.py

import json
import os
import sqlite3

from core.ai_usage_widget._platform import get_data_dir


def get_opencode_db_path() -> str:
    opencode_db = os.environ.get("OPENCODE_DB")
    if opencode_db:
        if opencode_db == ":memory:" or os.path.isabs(opencode_db):
            return opencode_db
        return os.path.join(get_data_dir(), "opencode", opencode_db)
    return os.path.join(get_data_dir(), "opencode", "opencode.db")


def _parse_model(raw: str | None) -> dict:
    if not raw:
        return {"id": "unknown", "provider": "unknown"}
    if raw.startswith("{"):
        try:
            obj = json.loads(raw)
            return {
                "id": obj.get("id", "unknown"),
                "provider": obj.get("providerID", "unknown"),
            }
        except (json.JSONDecodeError, TypeError):
            pass
    return {"id": raw, "provider": "unknown"}


def fetch_opencode_sessions(db_path: str | None = None) -> list[dict]:
    if db_path is None:
        db_path = get_opencode_db_path()

    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id, model,
            tokens_input, tokens_output, tokens_reasoning,
            tokens_cache_read, tokens_cache_write,
            cost, time_updated
        FROM session
        WHERE tokens_input > 0
        ORDER BY time_updated DESC
    """)

    sessions = []
    for row in cursor.fetchall():
        model_info = _parse_model(row["model"])
        sessions.append(
            {
                "id": row["id"],
                "model": row["model"] or "unknown",
                "model_id": model_info["id"],
                "provider": model_info["provider"],
                "tokens_input": row["tokens_input"] or 0,
                "tokens_output": row["tokens_output"] or 0,
                "tokens_reasoning": row["tokens_reasoning"] or 0,
                "tokens_cache_read": row["tokens_cache_read"] or 0,
                "tokens_cache_write": row["tokens_cache_write"] or 0,
                "cost": row["cost"] or 0,
                "timestamp": _parse_timestamp(row["time_updated"]),
            }
        )

    conn.close()
    return sessions


def _parse_timestamp(val) -> float:
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        ts = float(val)
        if ts > 1e12:
            ts = ts / 1000.0
        return ts
    try:
        from datetime import datetime

        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(val, fmt).timestamp()
            except ValueError:
                continue
        return datetime.fromisoformat(val).timestamp()
    except Exception:
        return 0
