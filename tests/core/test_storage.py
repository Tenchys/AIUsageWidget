import sqlite3

import pytest

from core.ai_usage_widget.storage import (
    _parse_model,
    _parse_timestamp,
    fetch_opencode_sessions,
    get_opencode_db_path,
)


class TestGetOpencodeDbPath:
    def test_default_path(self, mock_data_dir):
        path = get_opencode_db_path()
        assert path.endswith("opencode/opencode.db")

    def test_env_var_absolute(self, monkeypatch):
        monkeypatch.setenv("OPENCODE_DB", "/custom/path/db.sqlite")
        path = get_opencode_db_path()
        assert path == "/custom/path/db.sqlite"

    def test_env_var_memory(self, monkeypatch):
        monkeypatch.setenv("OPENCODE_DB", ":memory:")
        path = get_opencode_db_path()
        assert path == ":memory:"

    def test_env_var_relative(self, monkeypatch, mock_data_dir):
        monkeypatch.setenv("OPENCODE_DB", "custom.db")
        path = get_opencode_db_path()
        assert "opencode" in path
        assert path.endswith("custom.db")


class TestParseModel:
    def test_none(self):
        result = _parse_model(None)
        assert result == {"id": "unknown", "provider": "unknown"}

    def test_empty_string(self):
        result = _parse_model("")
        assert result["id"] == "unknown"

    def test_plain_string(self):
        result = _parse_model("deepseek-v4-flash")
        assert result["id"] == "deepseek-v4-flash"
        assert result["provider"] == "unknown"

    def test_json_object(self):
        raw = '{"id":"gpt-4o","providerID":"openai"}'
        result = _parse_model(raw)
        assert result["id"] == "gpt-4o"
        assert result["provider"] == "openai"

    def test_invalid_json(self):
        result = _parse_model("{invalid}")
        assert result["id"] == "{invalid}"


class TestParseTimestamp:
    def test_none(self):
        assert _parse_timestamp(None) == 0

    def test_int_seconds(self):
        result = _parse_timestamp(1000000)
        assert result == 1000000.0

    def test_int_milliseconds(self):
        result = _parse_timestamp(1000000000001)
        assert result == 1000000000.001

    def test_float(self):
        result = _parse_timestamp(1000000.5)
        assert result == 1000000.5

    def test_string_datetime(self):
        result = _parse_timestamp("2024-01-15 10:30:00")
        assert isinstance(result, float)
        assert result > 0

    def test_string_iso(self):
        result = _parse_timestamp("2024-01-15T10:30:00")
        assert isinstance(result, float)
        assert result > 0

    def test_invalid_string(self):
        result = _parse_timestamp("not-a-date")
        assert result == 0


class TestFetchOpencodeSessions:
    @pytest.fixture
    def db_with_data(self, tmp_path):
        db_path = tmp_path / "opencode.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session (
                id TEXT,
                model TEXT,
                tokens_input INTEGER,
                tokens_output INTEGER,
                tokens_reasoning INTEGER,
                tokens_cache_read INTEGER,
                tokens_cache_write INTEGER,
                cost REAL,
                time_updated INTEGER
            )
        """)
        conn.execute("""
            INSERT INTO session VALUES
            ('s1', 'deepseek-v4-flash', 1000, 500, 0, 0, 0, 0.00028, 1000000),
            ('s2', '{"id":"gpt-4o","providerID":"openai"}', 500, 200, 0, 0, 0, 0.00325,
             2000000),
            ('s3', 'ignored', 0, 0, 0, 0, 0, 0, 3000000)
        """)
        conn.commit()
        conn.close()
        return str(db_path)

    def test_fetch_returns_sessions_with_tokens(self, db_with_data):
        sessions = fetch_opencode_sessions(db_with_data)
        assert len(sessions) == 2

    def test_fetch_parses_model_json(self, db_with_data):
        sessions = fetch_opencode_sessions(db_with_data)
        gpt_session = [s for s in sessions if s["id"] == "s2"][0]
        assert gpt_session["model_id"] == "gpt-4o"
        assert gpt_session["provider"] == "openai"

    def test_empty_db(self, tmp_path):
        db_path = tmp_path / "empty.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session (
                id TEXT, model TEXT, tokens_input INTEGER,
                tokens_output INTEGER, tokens_reasoning INTEGER,
                tokens_cache_read INTEGER, tokens_cache_write INTEGER,
                cost REAL, time_updated INTEGER
            )
        """)
        conn.commit()
        conn.close()
        sessions = fetch_opencode_sessions(str(db_path))
        assert sessions == []

    def test_nonexistent_db(self):
        sessions = fetch_opencode_sessions("/nonexistent/path.db")
        assert sessions == []
