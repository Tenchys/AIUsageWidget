import time

from core.ai_usage_widget.pricing.opencode_go import LIMITS
from core.ai_usage_widget.windows import (
    WindowStatus,
    format_reset_time,
    get_reset_time_remaining,
    get_windows,
)


class TestWindowStatus:
    def test_dataclass_creation(self):
        ws = WindowStatus("5h", 12.0, 3.0, 9.0, 1000.0, 25.0)
        assert ws.name == "5h"
        assert ws.limit == 12.0
        assert ws.used == 3.0
        assert ws.remaining == 9.0
        assert ws.reset_at == 1000.0
        assert ws.percent == 25.0


class TestGetWindows:
    def test_no_sessions(self):
        windows = get_windows([])
        assert len(windows) == 3
        for w in windows:
            assert w.used == 0
            assert w.remaining == LIMITS[w.name]
            assert w.percent == 0

    def test_with_sessions_rolling(self, sample_sessions):
        go_sessions = [s for s in sample_sessions if s["provider"] == "opencode-go"]
        windows = get_windows(go_sessions)
        assert len(windows) == 3
        names = {w.name for w in windows}
        assert names == {"5h", "weekly", "monthly"}

    def test_with_subscription_start(self, sample_sessions):
        now = time.time()
        sub_start = now - 15 * 86400
        go_sessions = [s for s in sample_sessions if s["provider"] == "opencode-go"]
        windows = get_windows(go_sessions, subscription_start=sub_start)
        assert len(windows) == 3

    def test_percent_capped_at_100(self):
        sessions = [{"timestamp": time.time(), "cost": 100}]
        windows = get_windows(sessions)
        for w in windows:
            assert w.percent <= 100

    def test_custom_now(self):
        now = 1000000.0
        sessions = [{"timestamp": now - 100, "cost": 5.0}]
        windows = get_windows(sessions, now=now)
        assert len(windows) == 3


class TestGetResetTimeRemaining:
    def test_positive_remaining(self):
        result = get_reset_time_remaining(10000, now=5000)
        assert result == "1h 23m"

    def test_zero_remaining(self):
        result = get_reset_time_remaining(1000, now=2000)
        assert result == "ahora"

    def test_less_than_hour(self):
        result = get_reset_time_remaining(5000, now=4000)
        assert result == "16m"

    def test_exactly_hour(self):
        result = get_reset_time_remaining(8600, now=5000)
        assert result == "1h 0m"


class TestFormatResetTime:
    def test_format(self):
        result = format_reset_time(10000000)
        assert "/" in result
        assert ":" in result
