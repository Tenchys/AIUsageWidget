import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from core.ai_usage_widget._platform import get_user_agent

AUTH_PATH = os.path.expanduser("~/.codex/auth.json")
USAGE_URL = "https://chatgpt.com/backend-api/wham/usage"
TOKEN_URL = "https://auth.openai.com/oauth/token"


def get_usage() -> dict:
    try:
        if not os.path.exists(AUTH_PATH):
            return {
                "provider": "chatgpt",
                "error": (
                    "No se encontr\u00f3 ~/.codex/auth.json. "
                    "Necesitas iniciar sesi\u00f3n en Codex primero."
                ),
            }

        auth = _load_auth()
        account_id = auth["tokens"]["account_id"]
        access_token = _get_valid_token(auth)

        usage = _fetch_usage(access_token, account_id)
        return _parse_usage(usage)

    except Exception as e:
        return {
            "provider": "chatgpt",
            "error": f"Error al obtener datos de ChatGPT: {e}",
        }


def _load_auth() -> dict:
    with open(AUTH_PATH) as f:
        return json.load(f)


def _save_auth(auth: dict):
    with open(AUTH_PATH, "w") as f:
        json.dump(auth, f, indent=2)


def _decode_jwt(token: str) -> dict:
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        return {}


def _is_token_expired(token: str) -> bool:
    payload = _decode_jwt(token)
    exp = payload.get("exp", 0)
    return time.time() > exp - 60


def _get_valid_token(auth: dict) -> str:
    access_token = auth["tokens"]["access_token"]
    if not _is_token_expired(access_token):
        return access_token

    refresh_token = auth["tokens"]["refresh_token"]
    payload = _decode_jwt(access_token)
    client_id = payload.get("client_id")

    data = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
        }
    ).encode()

    req = urllib.request.Request(TOKEN_URL, data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("User-Agent", "Codex/1.0")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            auth["tokens"]["access_token"] = result["access_token"]
            if "refresh_token" in result:
                auth["tokens"]["refresh_token"] = result["refresh_token"]
            auth["last_refresh"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            _save_auth(auth)
            return result["access_token"]
    except Exception as e:
        raise Exception(f"No se pudo renovar el token: {e}")


def _fetch_usage(access_token: str, account_id: str) -> dict:
    req = urllib.request.Request(USAGE_URL)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("ChatGPT-Account-Id", account_id)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", get_user_agent())
    req.add_header("Origin", "https://chatgpt.com")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise Exception(f"HTTP {e.code}: {body[:200]}")


def _parse_usage(data: dict) -> dict:
    plan_type = data.get("plan_type", "free")
    plan_cost = {"plus": 20, "pro": 200, "free": 0}.get(plan_type)
    plan_name = plan_type.capitalize()

    rate_limit = data.get("rate_limit", {})
    primary = rate_limit.get("primary_window", {})
    secondary = rate_limit.get("secondary_window", {})

    windows = []
    if primary:
        is_5h = primary.get("limit_window_seconds") == 18000
        windows.append(
            {
                "name": "5h" if is_5h else "primary",
                "used_percent": primary.get("used_percent", 0),
                "limit_window": primary.get("limit_window_seconds", 0),
                "reset_after_seconds": primary.get("reset_after_seconds", 0),
                "reset_at": primary.get("reset_at", 0),
            }
        )
    if secondary:
        windows.append(
            {
                "name": "weekly",
                "used_percent": secondary.get("used_percent", 0),
                "limit_window": secondary.get("limit_window_seconds", 0),
                "reset_after_seconds": secondary.get("reset_after_seconds", 0),
                "reset_at": secondary.get("reset_at", 0),
            }
        )

    credits = data.get("credits", {})

    return {
        "provider": "chatgpt",
        "plan_type": plan_type,
        "plan_name": plan_name,
        "plan_cost": plan_cost,
        "windows": windows,
        "allowed": rate_limit.get("allowed", True),
        "limit_reached": rate_limit.get("limit_reached", False),
        "credits": {
            "has_credits": credits.get("has_credits", False),
            "unlimited": credits.get("unlimited", False),
            "balance": credits.get("balance"),
            "approx_local": credits.get("approx_local_messages"),
            "approx_cloud": credits.get("approx_cloud_messages"),
        },
    }
