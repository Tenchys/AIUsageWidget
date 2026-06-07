import json
import os
import time

import pytest


@pytest.fixture
def mock_config_dir(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    import core.ai_usage_widget._platform as platform_mod

    original = platform_mod.get_config_dir
    platform_mod.get_config_dir = lambda: str(config_dir)
    yield str(config_dir)
    platform_mod.get_config_dir = original


@pytest.fixture
def mock_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    import core.ai_usage_widget._platform as platform_mod

    original = platform_mod.get_data_dir
    platform_mod.get_data_dir = lambda: str(data_dir)
    yield str(data_dir)
    platform_mod.get_data_dir = original


@pytest.fixture
def mock_config_file(mock_config_dir):
    config_path = os.path.join(mock_config_dir, "config.json")
    data = {"subscription_start": 1000000.0}
    with open(config_path, "w") as f:
        json.dump(data, f)
    return config_path


@pytest.fixture
def sample_sessions():
    now = time.time()
    return [
        {
            "id": "s1",
            "model": "deepseek-v4-flash",
            "model_id": "deepseek-v4-flash",
            "provider": "opencode-go",
            "tokens_input": 1000,
            "tokens_output": 500,
            "tokens_reasoning": 0,
            "tokens_cache_read": 0,
            "tokens_cache_write": 0,
            "cost": 0.00028,
            "timestamp": now - 100,
        },
        {
            "id": "s2",
            "model": "deepseek-v4-pro",
            "model_id": "deepseek-v4-pro",
            "provider": "opencode-go",
            "tokens_input": 2000,
            "tokens_output": 1000,
            "tokens_reasoning": 100,
            "tokens_cache_read": 500,
            "tokens_cache_write": 0,
            "cost": 0.00731,
            "timestamp": now - 10000,
        },
        {
            "id": "s3",
            "model": '{"id":"gpt-4o","providerID":"openai"}',
            "model_id": "gpt-4o",
            "provider": "openai",
            "tokens_input": 500,
            "tokens_output": 200,
            "tokens_reasoning": 0,
            "tokens_cache_read": 0,
            "tokens_cache_write": 0,
            "cost": 0.00325,
            "timestamp": now - 50000,
        },
    ]
