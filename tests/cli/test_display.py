from cli.ai_usage_cli.display import _bar, _fmt_seconds, _print_header


class TestBar:
    def test_zero_percent(self):
        result = _bar(0)
        assert "░" in result
        assert "█" not in result

    def test_full_percent(self):
        result = _bar(100)
        assert "█" in result
        assert "░" not in result

    def test_mid_range(self):
        result = _bar(50)
        assert "█" in result
        assert "░" in result

    def test_threshold_green(self):
        result = _bar(50)
        assert "\033[92m" in result

    def test_threshold_yellow(self):
        result = _bar(80)
        assert "\033[93m" in result

    def test_threshold_red(self):
        result = _bar(95)
        assert "\033[91m" in result

    def test_custom_width(self):
        result = _bar(50, width=10)
        assert len(result) > 10

    def test_over_100(self):
        result = _bar(150)
        assert "█" * 20 in result


class TestFmtSeconds:
    def test_zero(self):
        assert _fmt_seconds(0) == "ahora"

    def test_negative(self):
        assert _fmt_seconds(-10) == "ahora"

    def test_minutes_only(self):
        assert _fmt_seconds(300) == "5m"

    def test_hours_and_minutes(self):
        assert _fmt_seconds(7260) == "2h 1m"

    def test_days_and_hours(self):
        assert _fmt_seconds(90000) == "1d 1h"


class TestPrintHeader:
    def test_output(self, capsys):
        _print_header("Test Title")
        captured = capsys.readouterr()
        assert "Test Title" in captured.out
        assert "──" in captured.out
