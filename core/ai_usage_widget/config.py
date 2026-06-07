# core/ai_usage_widget/config.py

import json
import os

from core.ai_usage_widget._platform import get_config_dir

CONFIG_PATH = os.path.join(get_config_dir(), "config.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def get_subscription_start() -> float | None:
    config = load_config()
    return config.get("subscription_start")


def set_subscription_start(ts: float):
    config = load_config()
    config["subscription_start"] = ts
    save_config(config)
