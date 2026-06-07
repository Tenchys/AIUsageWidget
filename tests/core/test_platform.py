from core.ai_usage_widget._platform import get_config_dir, get_data_dir, get_user_agent


class TestGetConfigDir:
    def test_default(self, monkeypatch):
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        result = get_config_dir()
        assert result.endswith("/.config/ai-usage")

    def test_with_xdg(self, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", "/custom/config")
        result = get_config_dir()
        assert result == "/custom/config/ai-usage"


class TestGetDataDir:
    def test_default(self, monkeypatch):
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)
        result = get_data_dir()
        assert result.endswith("/.local/share")

    def test_with_xdg(self, monkeypatch):
        monkeypatch.setenv("XDG_DATA_HOME", "/custom/data")
        result = get_data_dir()
        assert result == "/custom/data"


class TestGetUserAgent:
    def test_returns_string(self):
        result = get_user_agent()
        assert isinstance(result, str)
        assert "Mozilla" in result
