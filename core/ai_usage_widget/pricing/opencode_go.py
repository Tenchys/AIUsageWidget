# core/ai_usage_widget/pricing/opencode_go.py

PRICING = {
    "glm-5.1": {
        "input": 1.40,
        "output": 4.40,
        "cached_read": 0.26,
    },
    "glm-5": {
        "input": 1.00,
        "output": 3.20,
        "cached_read": 0.20,
    },
    "kimi-k2.6": {
        "input": 0.95,
        "output": 4.00,
        "cached_read": 0.16,
    },
    "kimi-k2.5": {
        "input": 0.60,
        "output": 3.00,
        "cached_read": 0.10,
    },
    "mimo-v2.5": {
        "input": 0.14,
        "output": 0.28,
        "cached_read": 0.0028,
    },
    "mimo-v2.5-pro": {
        "input": 1.74,
        "output": 3.48,
        "cached_read": 0.0145,
    },
    "minimax-m3": {
        "input": 0.60,
        "output": 2.40,
        "cached_read": 0.12,
        "cached_write": 0.75,
    },
    "minimax-m2.7": {
        "input": 0.30,
        "output": 1.20,
        "cached_read": 0.06,
        "cached_write": 0.375,
    },
    "minimax-m2.5": {
        "input": 0.30,
        "output": 1.20,
        "cached_read": 0.06,
        "cached_write": 0.375,
    },
    "qwen3.7-max": {
        "input": 2.50,
        "output": 7.50,
        "cached_read": 0.50,
        "cached_write": 3.125,
    },
    "qwen3.7-plus": {
        "input": 0.40,
        "output": 1.60,
        "cached_read": 0.04,
        "cached_write": 0.50,
    },
    "qwen3.6-plus": {
        "input": 0.50,
        "output": 3.00,
        "cached_read": 0.05,
        "cached_write": 0.625,
    },
    "deepseek-v4-pro": {
        "input": 1.74,
        "output": 3.48,
        "cached_read": 0.0145,
    },
    "deepseek-v4-flash": {
        "input": 0.14,
        "output": 0.28,
        "cached_read": 0.0028,
    },
}

LIMITS = {
    "5h": 12.00,
    "weekly": 30.00,
    "monthly": 60.00,
}

WINDOW_SECONDS = {
    "5h": 5 * 3600,
    "weekly": 7 * 86400,
    "monthly": 30 * 86400,
}
