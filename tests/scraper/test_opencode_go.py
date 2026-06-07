from scraper.opencode_go import (
    GoUsageData,
    _extract_from_html,
    _extract_server_function_id,
    _extract_usage,
    _extract_workspace_id,
    _parse_server_response,
    _safe_pct,
    _safe_reset,
)


class TestGoUsageData:
    def test_dataclass(self):
        data = GoUsageData(30.0, 5000, 50.0, 200000, 10.0, 500000, {})
        assert data.five_hour_pct == 30.0
        assert data.weekly_pct == 50.0
        assert data.monthly_pct == 10.0


class TestExtractUsage:
    def test_match_found(self):
        html = "rollingUsage...resetInSec:5000,usagePercent:30"
        result = _extract_usage(html, "rollingUsage")
        assert result == (5000, 30.0)

    def test_no_match(self):
        html = "<div>no data</div>"
        result = _extract_usage(html, "rollingUsage")
        assert result is None

    def test_multiple_digits(self):
        html = "weeklyUsage...resetInSec:604800,usagePercent:100"
        result = _extract_usage(html, "weeklyUsage")
        assert result == (604800, 100.0)


class TestExtractFromHtml:
    def test_all_present(self):
        html = (
            "rollingUsage.resetInSec:5000,usagePercent:30}"
            "weeklyUsage.resetInSec:604800,usagePercent:50}"
            "monthlyUsage.resetInSec:2592000,usagePercent:10"
        )
        result = _extract_from_html(html)
        assert result is not None
        assert result.five_hour_pct == 30.0
        assert result.weekly_pct == 50.0
        assert result.monthly_pct == 10.0

    def test_partial_present(self):
        html = "rollingUsage...resetInSec:5000,usagePercent:30"
        result = _extract_from_html(html)
        assert result is not None
        assert result.five_hour_pct == 30.0
        assert result.weekly_pct == 0
        assert result.monthly_pct == 0

    def test_none_present(self):
        result = _extract_from_html("<div>no data</div>")
        assert result is None


class TestExtractWorkspaceId:
    def test_from_json(self):
        html = '"workspace","id":"wrk_abc123"'
        result = _extract_workspace_id(html)
        assert result == "wrk_abc123"

    def test_from_path(self):
        html = "/workspace/wrk_xyz789"
        result = _extract_workspace_id(html)
        assert result == "wrk_xyz789"

    def test_plain_match(self):
        html = "wrk_def456"
        result = _extract_workspace_id(html)
        assert result == "wrk_def456"

    def test_no_match(self):
        result = _extract_workspace_id("<div>no id</div>")
        assert result is None


class TestExtractServerFunctionId:
    def test_full_url(self):
        html = (
            'src="/_server?id=abc123def456abc123def456abc123def456'
            'abc123def456abc123def456abc123def456abc1"'
        )
        result = _extract_server_function_id(html)
        assert result is not None
        assert len(result) == 64

    def test_no_match(self):
        result = _extract_server_function_id("<div>no id</div>")
        assert result is None


class TestParseServerResponse:
    def test_valid_response(self):
        data = {
            "rolling": {"used": 30, "limit": 100, "resetIn": 5000},
            "weekly": {"used": 50, "limit": 100, "resetIn": 604800},
            "monthly": {"used": 10, "limit": 100, "resetIn": 2592000},
            "limits": {},
        }
        result = _parse_server_response(data)
        assert result is not None
        assert result.five_hour_pct == 30.0
        assert result.weekly_pct == 50.0
        assert result.monthly_pct == 10.0

    def test_invalid_response(self):
        result = _parse_server_response({"error": "not found"})
        assert result is None

    def test_empty_data(self):
        result = _parse_server_response({})
        assert result is None


class TestSafePct:
    def test_valid(self):
        assert _safe_pct({"used": 30, "limit": 100}) == 30.0

    def test_zero_limit(self):
        assert _safe_pct({"used": 30, "limit": 0}) == 0

    def test_not_dict(self):
        assert _safe_pct("not dict") == 0

    def test_no_limit_key(self):
        assert _safe_pct({"used": 30}) == 3000.0


class TestSafeReset:
    def test_with_resetIn(self):
        assert _safe_reset({"resetIn": 5000}) == 5000

    def test_with_reset(self):
        assert _safe_reset({"reset": 3000}) == 3000

    def test_not_dict(self):
        assert _safe_reset("not dict") == 0
