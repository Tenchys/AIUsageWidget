# core/ai_usage_widget/config.py

import os
import json

CONFIG_PATH = os.path.expanduser("~/.config/ai-usage/config.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def get_openai_key() -> str:
    config = load_config()
    return config.get("openai_admin_key", "") or os.environ.get("OPENAI_ADMIN_KEY", "")


def set_openai_key(key: str):
    config = load_config()
    config["openai_admin_key"] = key
    save_config(config)


def get_subscription_start() -> float | None:
    config = load_config()
    return config.get("subscription_start")


def set_subscription_start(ts: float):
    config = load_config()
    config["subscription_start"] = ts
    save_config(config)
