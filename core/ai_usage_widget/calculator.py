# core/ai_usage_widget/calculator.py

from decimal import Decimal, ROUND_HALF_UP
from .pricing import opencode_go, openai


def _get_price(provider: str, model: str, token_type: str) -> float:
    if provider == "opencode_go":
        pricing = opencode_go.PRICING
        model = model.lower().replace("_", "-")
    elif provider == "openai":
        pricing = openai.PRICING
    else:
        raise ValueError(f"Unknown provider: {provider}")

    if model not in pricing:
        closest = _find_closest_model(model, pricing)
        if closest:
            model = closest
        else:
            return 0.0

    p = pricing[model]
    if token_type == "input":
        return p.get("input", 0.0)
    elif token_type == "output":
        return p.get("output", 0.0)
    elif token_type == "cached_read":
        return p.get("cached_read", p.get("cached_input", 0.0))
    elif token_type == "cached_write":
        return p.get("cached_write", 0.0)
    elif token_type == "reasoning":
        return p.get("output", 0.0)
    return 0.0


def _find_closest_model(model: str, pricing: dict) -> str | None:
    for key in pricing:
        if key in model or model in key:
            return key
    return None


def calculate_cost(
    provider: str,
    model: str,
    tokens_input: int = 0,
    tokens_output: int = 0,
    tokens_reasoning: int = 0,
    tokens_cache_read: int = 0,
    tokens_cache_write: int = 0,
) -> float:
    cost = 0.0
    cost += (tokens_input / 1_000_000) * _get_price(provider, model, "input")
    cost += (tokens_output / 1_000_000) * _get_price(provider, model, "output")
    cost += (tokens_reasoning / 1_000_000) * _get_price(provider, model, "reasoning")
    cost += (tokens_cache_read / 1_000_000) * _get_price(provider, model, "cached_read")
    cost += (tokens_cache_write / 1_000_000) * _get_price(provider, model, "cached_write")
    return round(cost, 6)


def calculate_cost_from_session(session: dict, provider: str = "opencode_go") -> float:
    model = session.get("model_id", session.get("model", ""))
    tokens_input = session.get("tokens_input", 0) or 0
    tokens_output = session.get("tokens_output", 0) or 0
    tokens_reasoning = session.get("tokens_reasoning", 0) or 0
    tokens_cache_read = session.get("tokens_cache_read", 0) or 0
    tokens_cache_write = session.get("tokens_cache_write", 0) or 0

    return calculate_cost(
        provider=provider,
        model=model,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        tokens_reasoning=tokens_reasoning,
        tokens_cache_read=tokens_cache_read,
        tokens_cache_write=tokens_cache_write,
    )
