# scraper/cookies.py

import os
import json
import time
import platform
import http.cookiejar
from core.ai_usage_widget._platform import get_config_dir

COOKIES_PATH = os.path.join(get_config_dir(), "cookies.json")


def _cookie_entry(name: str, value: str, expires: int | None) -> dict[str, str | int | None]:
    return {"name": name, "value": value, "expires": expires}


def _load_from_browser() -> list[dict[str, str | int | None]] | None:
    try:
        import browser_cookie3
    except ImportError:
        return None

    browsers = [
        ("chrome", browser_cookie3.chrome),
        ("firefox", browser_cookie3.firefox),
        ("brave", browser_cookie3.brave),
        ("edge", browser_cookie3.edge),
        ("chromium", browser_cookie3.chromium),
    ]

    if platform.system() != "Linux":
        browsers.insert(0, ("safari", browser_cookie3.safari))

    for name, loader in browsers:
        try:
            cj = loader(domain_name="opencode.ai")
            cookies = []
            for cookie in cj:
                if cookie.domain and "opencode.ai" in cookie.domain:
                    cookies.append(_cookie_entry(cookie.name, cookie.value, cookie.expires))
            if cookies:
                return cookies
        except Exception:
            continue

    return None


def get_cookies() -> dict[str, str] | None:
    saved = _load_saved()
    if saved:
        return saved

    browser_cookies = _load_from_browser()
    if not browser_cookies:
        return None

    save_cookie_entries(browser_cookies)
    return {cookie["name"]: str(cookie["value"]) for cookie in browser_cookies}


def _load_saved() -> dict[str, str] | None:
    if os.path.exists(COOKIES_PATH):
        try:
            with open(COOKIES_PATH) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {k: str(v) for k, v in data.items()}
                if isinstance(data, list):
                    return {
                        item["name"]: str(item["value"])
                        for item in data
                        if isinstance(item, dict) and "name" in item and "value" in item
                    }
                return None
        except Exception:
            return None
    return None


def save_cookies(cookies: dict[str, str]):
    save_cookie_entries([
        _cookie_entry(name, value, None)
        for name, value in cookies.items()
    ])


def save_cookie_entries(cookies: list[dict[str, str | int | None]]):
    os.makedirs(os.path.dirname(COOKIES_PATH), exist_ok=True)
    with open(COOKIES_PATH, "w") as f:
        json.dump(cookies, f)


def clear_cookies():
    if os.path.exists(COOKIES_PATH):
        os.remove(COOKIES_PATH)


def cookies_to_header(cookies: dict[str, str]) -> str:
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


def _load_saved_entries() -> list[dict[str, str | int | None]] | None:
    if os.path.exists(COOKIES_PATH):
        try:
            with open(COOKIES_PATH) as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return None
        except Exception:
            return None
    return None


def get_saved_expiry() -> int | None:
    entries = _load_saved_entries()
    if not entries:
        return None
    expires_values = [
        e.get("expires") for e in entries
        if isinstance(e.get("expires"), (int, float))
    ]
    if not expires_values:
        return None
    return int(max(expires_values))


def is_expired(expires: int | None) -> bool:
    if expires is None:
        return False
    return time.time() > expires


def format_expiry_date(expires: int | None) -> str | None:
    if expires is None:
        return None
    import datetime
    dt = datetime.datetime.fromtimestamp(expires)
    return dt.strftime("%d/%m/%Y %H:%M")
