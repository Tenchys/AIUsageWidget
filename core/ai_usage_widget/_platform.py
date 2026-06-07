import os
import platform


def get_config_dir() -> str:
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return os.path.join(xdg_config, "ai-usage")
    return os.path.expanduser("~/.config/ai-usage")


def get_data_dir() -> str:
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return xdg_data
    return os.path.expanduser("~/.local/share")


def get_user_agent() -> str:
    if platform.system() == "Linux":
        return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
