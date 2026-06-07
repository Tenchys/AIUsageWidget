import sys
from unittest.mock import MagicMock, patch

from cli.ai_usage_cli.main import main


class TestCliIntegration:
    @patch("cli.ai_usage_cli.main.opencode")
    @patch("cli.ai_usage_cli.main.chatgpt")
    def test_status_command_full_flow(self, mock_chatgpt, mock_opencode, capsys):
        mock_opencode.get_usage.return_value = {
            "provider": "opencode_go",
            "total_sessions": 10,
            "total_cost": 1.2345,
            "source": "local",
            "cookie_expiry": None,
            "windows": [
                MagicMock(
                    name="5h",
                    limit=12.0,
                    used=3.0,
                    remaining=9.0,
                    reset_at=9999999999,
                    percent=25.0,
                ),
                MagicMock(
                    name="weekly",
                    limit=30.0,
                    used=15.0,
                    remaining=15.0,
                    reset_at=9999999999,
                    percent=50.0,
                ),
                MagicMock(
                    name="monthly",
                    limit=60.0,
                    used=6.0,
                    remaining=54.0,
                    reset_at=9999999999,
                    percent=10.0,
                ),
            ],
            "models": {},
        }
        mock_chatgpt.get_usage.return_value = {
            "provider": "chatgpt",
            "plan_name": "Plus",
            "plan_cost": 20,
            "allowed": True,
            "limit_reached": False,
            "windows": [],
            "credits": {"has_credits": False},
        }

        test_args = ["ai-usage", "status"]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        assert "OpenCode Go" in captured.out
        assert "ChatGPT Plus" in captured.out

    @patch("cli.ai_usage_cli.main.opencode")
    def test_models_command_full_flow(self, mock_opencode, capsys):
        mock_opencode.get_usage.return_value = {
            "provider": "opencode_go",
            "models": {
                "deepseek-v4-flash": {
                    "sessions": 5,
                    "tokens_input": 10000,
                    "tokens_output": 5000,
                    "cost": 0.01,
                },
                "deepseek-v4-pro": {
                    "sessions": 3,
                    "tokens_input": 6000,
                    "tokens_output": 3000,
                    "cost": 0.02,
                },
            },
        }

        test_args = ["ai-usage", "models"]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        assert "Modelos usados" in captured.out
        assert "deepseek-v4-flash" in captured.out
        assert "deepseek-v4-pro" in captured.out
