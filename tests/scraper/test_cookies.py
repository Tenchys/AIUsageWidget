import json
import os
import time
from unittest.mock import patch

from scraper.cookies import (
    _cookie_entry,
    _load_saved,
    _load_saved_entries,
    clear_cookies,
    cookies_to_header,
    format_expiry_date,
    get_cookies,
    get_saved_expiry,
    is_expired,
    save_cookie_entries,
    save_cookies,
)


def test_cookie_entry():
    entry = _cookie_entry("name", "value", 1000)
    assert entry == {"name": "name", "value": "value", "expires": 1000}


def test_cookies_to_header():
    cookies = {"session": "abc", "token": "xyz"}
    header = cookies_to_header(cookies)
    assert "session=abc" in header
    assert "token=xyz" in header


class TestGetCookies:
    def test_load_saved_dict_format(self):
        with patch("scraper.cookies._load_saved") as mock_saved:
            mock_saved.return_value = {"session": "abc", "token": "xyz"}
            result = get_cookies()
            assert result == {"session": "abc", "token": "xyz"}

    def test_no_saved_falls_to_browser(self):
        with patch("scraper.cookies._load_saved", return_value=None):
            with patch("scraper.cookies._load_from_browser", return_value=None):
                result = get_cookies()
                assert result is None

    def test_load_from_browser_saves_and_returns(self):
        browser_cookies = [
            {"name": "session", "value": "browser_val", "expires": 9999999999},
        ]
        with patch("scraper.cookies._load_saved", return_value=None):
            with patch(
                "scraper.cookies._load_from_browser", return_value=browser_cookies
            ):
                with patch("scraper.cookies.save_cookie_entries") as mock_save:
                    result = get_cookies()
                    assert result == {"session": "browser_val"}
                    mock_save.assert_called_once_with(browser_cookies)

    def test_load_saved_returns_none_on_exception(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "cookies.json")
        with open(fake_path, "w") as f:
            f.write("invalid json")
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            with patch("scraper.cookies._load_from_browser", return_value=None):
                result = get_cookies()
                assert result is None


class TestSaveAndClear:
    def test_save_cookies(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "cookies.json")
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            save_cookies({"custom": "value"})
            with open(fake_path) as f:
                data = json.load(f)
        assert isinstance(data, list)
        assert data[0]["name"] == "custom"
        assert data[0]["value"] == "value"

    def test_save_cookie_entries(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "cookies.json")
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            entries = [{"name": "a", "value": "1", "expires": None}]
            save_cookie_entries(entries)
            with open(fake_path) as f:
                data = json.load(f)
        assert data == entries

    def test_clear_cookies(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "cookies.json")
        with open(fake_path, "w") as f:
            json.dump([], f)
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            assert os.path.exists(fake_path)
            clear_cookies()
            assert not os.path.exists(fake_path)

    def test_clear_when_no_file(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "nonexistent.json")
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            clear_cookies()


class TestExpiry:
    def test_get_saved_expiry(self, tmp_path):
        cookies = [
            {"name": "s", "value": "v", "expires": int(time.time()) + 86400},
        ]
        fake_path = os.path.join(str(tmp_path), "cookies.json")
        with open(fake_path, "w") as f:
            json.dump(cookies, f)
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            expiry = get_saved_expiry()
            assert isinstance(expiry, int)

    def test_get_saved_expiry_no_file(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "cookies.json")
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            assert get_saved_expiry() is None

    def test_is_expired_false(self):
        future = int(time.time()) + 3600
        assert is_expired(future) is False

    def test_is_expired_true(self):
        past = int(time.time()) - 3600
        assert is_expired(past) is True

    def test_is_expired_none(self):
        assert is_expired(None) is False

    def test_format_expiry_date(self):
        result = format_expiry_date(1000000000)
        assert isinstance(result, str)

    def test_format_expiry_date_none(self):
        assert format_expiry_date(None) is None


class TestLoadSaved:
    def test_load_saved_nonexistent(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "nonexistent.json")
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            assert _load_saved() is None

    def test_load_saved_invalid_json(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "cookies.json")
        with open(fake_path, "w") as f:
            f.write("not json")
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            assert _load_saved() is None

    def test_load_saved_entries(self, tmp_path):
        cookies = [
            {"name": "s", "value": "v", "expires": int(time.time()) + 86400},
        ]
        fake_path = os.path.join(str(tmp_path), "cookies.json")
        with open(fake_path, "w") as f:
            json.dump(cookies, f)
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            entries = _load_saved_entries()
            assert entries is not None
            assert len(entries) == 1

    def test_load_saved_entries_nonexistent(self, tmp_path):
        fake_path = os.path.join(str(tmp_path), "nonexistent.json")
        with patch("scraper.cookies.COOKIES_PATH", fake_path):
            assert _load_saved_entries() is None
