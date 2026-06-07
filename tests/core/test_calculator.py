from core.ai_usage_widget.calculator import (
    _find_closest_model,
    _get_price,
    calculate_cost,
    calculate_cost_from_session,
)


class TestGetPrice:
    def test_opencode_go_known_model(self):
        price = _get_price("opencode_go", "deepseek-v4-flash", "input")
        assert price == 0.14

    def test_opencode_go_model_with_underscore(self):
        price = _get_price("opencode_go", "deepseek_v4_flash", "input")
        assert price == 0.14

    def test_openai_known_model(self):
        price = _get_price("openai", "gpt-4o", "input")
        assert price == 2.50

    def test_unknown_provider(self):
        import pytest

        with pytest.raises(ValueError, match="Unknown provider"):
            _get_price("unknown_provider", "model", "input")

    def test_unknown_model_returns_zero(self):
        price = _get_price("opencode_go", "nonexistent-model", "input")
        assert price == 0.0

    def test_cached_read_falls_back_to_cached_input(self):
        price = _get_price("openai", "gpt-4o", "cached_read")
        assert price == 1.25

    def test_reasoning_uses_output_price(self):
        price = _get_price("opencode_go", "deepseek-v4-flash", "reasoning")
        assert price == 0.28

    def test_unknown_token_type(self):
        price = _get_price("opencode_go", "deepseek-v4-flash", "unknown_type")
        assert price == 0.0


class TestFindClosestModel:
    def test_exact_match(self):
        pricing = {"deepseek-v4-flash": {}, "gpt-4o": {}}
        result = _find_closest_model("deepseek-v4-flash", pricing)
        assert result == "deepseek-v4-flash"

    def test_partial_match_model_in_key(self):
        pricing = {"deepseek-v4-flash": {}, "gpt-4o": {}}
        result = _find_closest_model("v4-flash", pricing)
        assert result == "deepseek-v4-flash"

    def test_partial_match_key_in_model(self):
        pricing = {"deepseek-v4-flash": {}, "gpt-4o": {}}
        result = _find_closest_model("deepseek-v4-flash-xyz", pricing)
        assert result == "deepseek-v4-flash"

    def test_no_match(self):
        pricing = {"gpt-4o": {}}
        result = _find_closest_model("nonexistent", pricing)
        assert result is None

    def test_empty_pricing(self):
        result = _find_closest_model("model", {})
        assert result is None


class TestCalculateCost:
    def test_basic_cost(self):
        cost = calculate_cost(
            "opencode_go", "deepseek-v4-flash", tokens_input=1_000_000
        )
        assert cost == 0.14

    def test_full_cost(self):
        cost = calculate_cost(
            "opencode_go",
            "deepseek-v4-flash",
            tokens_input=1_000_000,
            tokens_output=500_000,
        )
        assert cost == 0.14 + 0.14

    def test_zero_tokens(self):
        cost = calculate_cost("opencode_go", "deepseek-v4-flash")
        assert cost == 0.0

    def test_with_reasoning_and_cache(self):
        cost = calculate_cost(
            "opencode_go",
            "deepseek-v4-pro",
            tokens_input=1_000_000,
            tokens_output=500_000,
            tokens_reasoning=100_000,
            tokens_cache_read=200_000,
        )
        expected = (
            (1_000_000 / 1_000_000) * 1.74
            + (500_000 / 1_000_000) * 3.48
            + (100_000 / 1_000_000) * 3.48
            + (200_000 / 1_000_000) * 0.0145
        )
        assert cost == round(expected, 6)

    def test_unknown_model_returns_zero(self):
        cost = calculate_cost("opencode_go", "nonexistent", tokens_input=1_000_000)
        assert cost == 0.0


class TestCalculateCostFromSession:
    def test_with_full_session(self):
        session = {
            "model_id": "deepseek-v4-flash",
            "tokens_input": 1000,
            "tokens_output": 500,
        }
        cost = calculate_cost_from_session(session, "opencode_go")
        expected = (1000 / 1_000_000) * 0.14 + (500 / 1_000_000) * 0.28
        assert cost == round(expected, 6)

    def test_falls_back_to_model_key(self):
        session = {"model": "deepseek-v4-flash", "tokens_input": 1000}
        cost = calculate_cost_from_session(session, "opencode_go")
        assert cost > 0

    def test_none_tokens(self):
        session = {
            "model_id": "deepseek-v4-flash",
            "tokens_input": None,
            "tokens_output": None,
        }
        cost = calculate_cost_from_session(session, "opencode_go")
        assert cost == 0.0
