import json
import os

from core.ai_usage_widget.config import (
    CONFIG_PATH,
    get_subscription_start,
    load_config,
    save_config,
    set_subscription_start,
)


class TestConfig:
    def test_load_empty_when_no_file(self, mock_config_dir):
        original_path = CONFIG_PATH
        import core.ai_usage_widget.config as config_mod

        config_mod.CONFIG_PATH = os.path.join(mock_config_dir, "config.json")
        try:
            result = load_config()
            assert result == {}
        finally:
            config_mod.CONFIG_PATH = original_path

    def test_load_existing_file(self, mock_config_file):
        import core.ai_usage_widget.config as config_mod

        original = config_mod.CONFIG_PATH
        config_mod.CONFIG_PATH = mock_config_file
        try:
            result = load_config()
            assert result.get("subscription_start") == 1000000.0
        finally:
            config_mod.CONFIG_PATH = original

    def test_save_and_reload(self, mock_config_dir):
        import core.ai_usage_widget.config as config_mod

        config_path = os.path.join(mock_config_dir, "config.json")
        original = config_mod.CONFIG_PATH
        config_mod.CONFIG_PATH = config_path
        try:
            save_config({"custom_key": "custom_value"})
            with open(config_path) as f:
                data = json.load(f)
            assert data["custom_key"] == "custom_value"
        finally:
            config_mod.CONFIG_PATH = original

    def test_get_subscription_start(self, mock_config_file):
        import core.ai_usage_widget.config as config_mod

        original = config_mod.CONFIG_PATH
        config_mod.CONFIG_PATH = mock_config_file
        try:
            result = get_subscription_start()
            assert result == 1000000.0
        finally:
            config_mod.CONFIG_PATH = original

    def test_get_subscription_start_none(self, mock_config_dir):
        import core.ai_usage_widget.config as config_mod

        config_path = os.path.join(mock_config_dir, "config.json")
        original = config_mod.CONFIG_PATH
        config_mod.CONFIG_PATH = config_path
        try:
            result = get_subscription_start()
            assert result is None
        finally:
            config_mod.CONFIG_PATH = original

    def test_set_subscription_start(self, mock_config_dir):
        import core.ai_usage_widget.config as config_mod

        config_path = os.path.join(mock_config_dir, "config.json")
        original = config_mod.CONFIG_PATH
        config_mod.CONFIG_PATH = config_path
        try:
            set_subscription_start(5000000.0)
            result = get_subscription_start()
            assert result == 5000000.0
        finally:
            config_mod.CONFIG_PATH = original
