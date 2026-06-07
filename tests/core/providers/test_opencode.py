import time
from unittest.mock import MagicMock, patch

from core.ai_usage_widget.providers.opencode import _try_scraper, get_usage
from scraper.errors import CookieExpiredError


class TestTryScraper:
    @patch("scraper.cookies.get_saved_expiry")
    @patch("scraper.cookies.is_expired")
    @patch("scraper.cookies.get_cookies")
    @patch("scraper.opencode_go.fetch_go_usage")
    def test_success(
        self, mock_fetch, mock_get_cookies, mock_is_expired, mock_get_expiry
    ):
        mock_get_expiry.return_value = 9999999999
        mock_is_expired.return_value = False
        mock_get_cookies.return_value = {"session": "abc"}
        with patch("scraper.cookies.cookies_to_header", return_value="session=abc"):
            mock_fetch.return_value = MagicMock()
            result = _try_scraper()
            assert result is not None
            mock_fetch.assert_called_once_with("session=abc")

    @patch("scraper.cookies.get_saved_expiry")
    @patch("scraper.cookies.is_expired")
    def test_expired_cookie_raises(self, mock_is_expired, mock_get_expiry):
        mock_get_expiry.return_value = 1000
        mock_is_expired.return_value = True
        with patch(
            "scraper.cookies.format_expiry_date", return_value="01/01/2024 00:00"
        ):
            import pytest

            with pytest.raises(CookieExpiredError):
                _try_scraper()

    @patch("scraper.cookies.get_saved_expiry")
    @patch("scraper.cookies.is_expired")
    @patch("scraper.cookies.get_cookies")
    def test_no_cookies_returns_none(
        self, mock_get_cookies, mock_is_expired, mock_get_expiry
    ):
        mock_get_expiry.return_value = 9999999999
        mock_is_expired.return_value = False
        mock_get_cookies.return_value = None
        result = _try_scraper()
        assert result is None


class TestGetUsage:
    @patch("core.ai_usage_widget.providers.opencode.fetch_opencode_sessions")
    @patch("core.ai_usage_widget.providers.opencode._try_scraper")
    def test_scraper_success(self, mock_scraper, mock_fetch, sample_sessions):
        mock_fetch.return_value = sample_sessions
        mock_data = MagicMock()
        mock_data.five_hour_pct = 30.0
        mock_data.five_hour_reset_seconds = 5000
        mock_data.weekly_pct = 50.0
        mock_data.weekly_reset_seconds = 200000
        mock_data.monthly_pct = 10.0
        mock_data.monthly_reset_seconds = 500000
        mock_scraper.return_value = mock_data

        with (
            patch("scraper.cookies.get_saved_expiry", return_value=None),
            patch("scraper.cookies.format_expiry_date", return_value=None),
        ):
            result = get_usage()
        assert result["source"] == "web"
        assert result["provider"] == "opencode_go"
        assert len(result["windows"]) == 3

    @patch("core.ai_usage_widget.providers.opencode.fetch_opencode_sessions")
    @patch("core.ai_usage_widget.providers.opencode._try_scraper")
    def test_cookie_expired_error(self, mock_scraper, mock_fetch, sample_sessions):
        mock_fetch.return_value = sample_sessions
        mock_scraper.side_effect = CookieExpiredError("01/01/2024 00:00")
        result = get_usage()
        assert "error" in result
        assert "expirada" in result["error"]

    @patch("core.ai_usage_widget.providers.opencode.fetch_opencode_sessions")
    @patch("core.ai_usage_widget.providers.opencode._try_scraper")
    @patch("core.ai_usage_widget.providers.opencode.get_subscription_start")
    def test_fallback_local_no_subscription(
        self, mock_sub_start, mock_scraper, mock_fetch, sample_sessions
    ):
        mock_fetch.return_value = sample_sessions
        mock_scraper.return_value = None
        mock_sub_start.return_value = None
        with (
            patch("scraper.cookies.get_saved_expiry", return_value=None),
            patch("scraper.cookies.format_expiry_date", return_value=None),
        ):
            result = get_usage()
        assert result["source"] == "local"
        assert "windows" in result

    @patch("core.ai_usage_widget.providers.opencode.fetch_opencode_sessions")
    @patch("core.ai_usage_widget.providers.opencode._try_scraper")
    @patch("core.ai_usage_widget.providers.opencode.get_subscription_start")
    def test_fallback_local_with_subscription(
        self, mock_sub_start, mock_scraper, mock_fetch, sample_sessions
    ):
        mock_fetch.return_value = sample_sessions
        mock_scraper.return_value = None
        mock_sub_start.return_value = time.time() - 15 * 86400
        with (
            patch("scraper.cookies.get_saved_expiry", return_value=None),
            patch("scraper.cookies.format_expiry_date", return_value=None),
        ):
            result = get_usage()
        assert result["source"] == "local"

    @patch("core.ai_usage_widget.providers.opencode.fetch_opencode_sessions")
    @patch("core.ai_usage_widget.providers.opencode._try_scraper")
    def test_models_aggregation(self, mock_scraper, mock_fetch, sample_sessions):
        mock_fetch.return_value = sample_sessions
        mock_scraper.return_value = None
        with (
            patch(
                "core.ai_usage_widget.providers.opencode.get_subscription_start",
                return_value=None,
            ),
            patch("scraper.cookies.get_saved_expiry", return_value=None),
            patch("scraper.cookies.format_expiry_date", return_value=None),
        ):
            result = get_usage()
        assert "models" in result
        assert "deepseek-v4-flash" in result["models"]
        assert "deepseek-v4-pro" in result["models"]
