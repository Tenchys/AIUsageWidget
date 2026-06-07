import json
import time

from core.ai_usage_widget.providers.chatgpt import (
    _decode_jwt,
    _is_token_expired,
    _parse_usage,
)


class TestDecodeJwt:
    def test_valid_token(self):
        import base64

        payload = json.dumps({"sub": "user1", "exp": 9999999999}).encode()
        encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
        token = f"header.{encoded}.signature"
        result = _decode_jwt(token)
        assert result["sub"] == "user1"

    def test_invalid_token(self):
        result = _decode_jwt("invalid")
        assert result == {}

    def test_empty_token(self):
        result = _decode_jwt("")
        assert result == {}


class TestIsTokenExpired:
    def test_not_expired(self, monkeypatch):
        import base64

        far_future = int(time.time()) + 3600
        payload = json.dumps({"exp": far_future}).encode()
        encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
        token = f"h.{encoded}.s"
        assert _is_token_expired(token) is False

    def test_expired(self, monkeypatch):
        import base64

        past = int(time.time()) - 3600
        payload = json.dumps({"exp": past}).encode()
        encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
        token = f"h.{encoded}.s"
        assert _is_token_expired(token) is True

    def test_no_exp_field(self):
        import base64

        payload = json.dumps({"sub": "user"}).encode()
        encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
        token = f"h.{encoded}.s"
        assert _is_token_expired(token) is True


class TestParseUsage:
    def test_free_plan(self):
        data = {"plan_type": "free"}
        result = _parse_usage(data)
        assert result["plan_name"] == "Free"
        assert result["plan_cost"] == 0
        assert result["windows"] == []

    def test_plus_plan_with_windows(self):
        data = {
            "plan_type": "plus",
            "rate_limit": {
                "allowed": True,
                "primary_window": {
                    "used_percent": 45.0,
                    "limit_window_seconds": 18000,
                    "reset_after_seconds": 7200,
                    "reset_at": 1000000,
                },
                "secondary_window": {
                    "used_percent": 30.0,
                    "limit_window_seconds": 604800,
                    "reset_after_seconds": 432000,
                    "reset_at": 2000000,
                },
            },
        }
        result = _parse_usage(data)
        assert result["plan_name"] == "Plus"
        assert result["plan_cost"] == 20
        assert len(result["windows"]) == 2
        assert result["windows"][0]["name"] == "5h"
        assert result["windows"][1]["name"] == "weekly"

    def test_with_credits(self):
        data = {
            "plan_type": "plus",
            "credits": {
                "has_credits": True,
                "unlimited": False,
                "balance": "5.00",
                "approx_local_messages": [5, 10],
                "approx_cloud_messages": [3, 10],
            },
        }
        result = _parse_usage(data)
        assert result["credits"]["has_credits"] is True
        assert result["credits"]["balance"] == "5.00"

    def test_limit_reached(self):
        data = {
            "plan_type": "plus",
            "rate_limit": {
                "allowed": False,
                "limit_reached": True,
            },
        }
        result = _parse_usage(data)
        assert result["allowed"] is False
        assert result["limit_reached"] is True
