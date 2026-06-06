# scraper/opencode_go.py

import re
import json
import urllib.request
import urllib.error
from dataclasses import dataclass


@dataclass
class GoUsageData:
    five_hour_pct: float
    five_hour_reset_seconds: int
    weekly_pct: float
    weekly_reset_seconds: int
    monthly_pct: float
    monthly_reset_seconds: int
    raw_data: dict


def fetch_go_usage(cookie_header: str) -> GoUsageData | None:
    text = _fetch_go_page(cookie_header)
    if not text:
        return None

    data = _extract_from_html(text)
    if data:
        return data

    sid = _extract_server_function_id(text)
    wid = _extract_workspace_id(text)
    if sid and wid:
        return _call_server_function(cookie_header, sid, wid)

    return None


def _fetch_go_page(cookie_header: str) -> str | None:
    from http.cookiejar import Cookie, CookieJar
    from urllib.parse import urlparse

    cj = CookieJar()
    for item in cookie_header.split(";"):
        item = item.strip()
        if "=" in item:
            name, value = item.split("=", 1)
            cj.set_cookie(Cookie(
                version=0, name=name, value=value, port=None, port_specified=False,
                domain="opencode.ai", domain_specified=True, domain_initial_dot=False,
                path="/", path_specified=True, secure=True, expires=None,
                discard=False, comment=None, comment_url=None, rest={},
            ))

    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPRedirectHandler(),
    )

    req = urllib.request.Request("https://opencode.ai/auth")
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    req.add_header("Accept", "text/html,application/xhtml+xml")

    try:
        resp = opener.open(req, timeout=15)
        final_url = resp.geturl()
        body = resp.read().decode("utf-8", errors="replace")

        if "/workspace/" not in final_url:
            workspace_match = re.search(r'/workspace/(wrk_[a-zA-Z0-9]+)', body)
            if workspace_match:
                wid = workspace_match.group(1)
                go_url = f"https://opencode.ai/workspace/{wid}/go"
                req2 = urllib.request.Request(go_url)
                req2.add_header("User-Agent", req.get_header("User-Agent") or "")
                resp2 = opener.open(req2, timeout=15)
                body = resp2.read().decode("utf-8", errors="replace")
        elif "/go" not in final_url:
            go_url = final_url.rstrip("/") + "/go"
            req2 = urllib.request.Request(go_url)
            req2.add_header("User-Agent", req.get_header("User-Agent") or "")
            resp2 = opener.open(req2, timeout=15)
            body = resp2.read().decode("utf-8", errors="replace")

        return body

    except Exception as e:
        return None


def _extract_from_html(html: str) -> GoUsageData | None:
    roll = _extract_usage(html, "rollingUsage")
    week = _extract_usage(html, "weeklyUsage")
    month = _extract_usage(html, "monthlyUsage")

    if not roll and not week and not month:
        return None

    return GoUsageData(
        five_hour_pct=roll[1] if roll else 0,
        five_hour_reset_seconds=roll[0] if roll else 0,
        weekly_pct=week[1] if week else 0,
        weekly_reset_seconds=week[0] if week else 0,
        monthly_pct=month[1] if month else 0,
        monthly_reset_seconds=month[0] if month else 0,
        raw_data={},
    )


def _extract_usage(html: str, key: str) -> tuple[int, float] | None:
    pattern = rf'{key}[^}}]*resetInSec:(\d+),usagePercent:(\d+)'
    m = re.search(pattern, html)
    if m:
        return int(m.group(1)), float(m.group(2))
    return None


def _extract_workspace_id(html: str) -> str | None:
    match = re.search(r'"workspace","id":"(wrk_[a-zA-Z0-9]+)"', html)
    if match:
        return match.group(1)
    match = re.search(r'/(workspace)/(wrk_[a-zA-Z0-9]+)', html)
    if match:
        return match.group(2)
    match = re.search(r'wrk_[a-zA-Z0-9]+', html)
    return match.group(0) if match else None


def _extract_server_function_id(html: str) -> str | None:
    patterns = [
        r'/_server\?id=([a-f0-9]{64})',
        r'_server\?id=([a-f0-9]{64})',
        r'"([a-f0-9]{64})"',
    ]
    for p in patterns:
        matches = re.findall(p, html)
        if matches:
            return matches[0]
    return None


def _call_server_function(cookie_header: str, server_id: str, workspace_id: str) -> GoUsageData | None:
    url = f"https://opencode.ai/_server"
    body = json.dumps({
        "t": {
            "t": 9,
            "i": 0,
            "l": 1,
            "a": [{"t": 1, "s": workspace_id}],
            "o": 0,
        },
        "f": 31,
        "m": [],
    })

    req = urllib.request.Request(url)
    req.add_header("Cookie", cookie_header)
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Server-Id", server_id)
    req.add_header("X-Server-Instance", "server-fn:0")
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    req.data = body.encode()

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = resp.read().decode("utf-8", errors="replace")
            data = json.loads(result)
            return _parse_server_response(data)
    except Exception:
        return None


def _parse_server_response(data: dict) -> GoUsageData | None:
    try:
        if "rolling" in data:
            r = data.get("rolling", {})
            w = data.get("weekly", {})
            m = data.get("monthly", {})
            limits = data.get("limits", {})
            return GoUsageData(
                five_hour_pct=_safe_pct(r),
                five_hour_reset_seconds=_safe_reset(r),
                weekly_pct=_safe_pct(w),
                weekly_reset_seconds=_safe_reset(w),
                monthly_pct=_safe_pct(m),
                monthly_reset_seconds=_safe_reset(m),
                raw_data=data,
            )
    except Exception:
        pass
    return None


def _safe_pct(obj: dict) -> float:
    if isinstance(obj, dict):
        used = obj.get("used", 0)
        limit = obj.get("limit", 1)
        if limit > 0:
            return round(used / limit * 100, 1)
    return 0


def _safe_reset(obj: dict) -> int:
    if isinstance(obj, dict):
        return obj.get("resetIn", obj.get("reset", 0))
    return 0
