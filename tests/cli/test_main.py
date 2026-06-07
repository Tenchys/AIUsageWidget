import sys
from unittest.mock import MagicMock, patch

from cli.ai_usage_cli.main import cmd_models, cmd_reset, cmd_setup, cmd_status, main


class TestMain:
    def test_no_args_calls_status(self):
        test_args = ["ai-usage"]
        with patch.object(sys, "argv", test_args):
            with patch("cli.ai_usage_cli.main.cmd_status") as mock:
                main()
                mock.assert_called_once()

    def test_status_command(self):
        test_args = ["ai-usage", "status"]
        with patch.object(sys, "argv", test_args):
            with patch("cli.ai_usage_cli.main.cmd_status") as mock:
                main()
                mock.assert_called_once()

    def test_models_command(self):
        test_args = ["ai-usage", "models"]
        with patch.object(sys, "argv", test_args):
            with patch("cli.ai_usage_cli.main.cmd_models") as mock:
                main()
                mock.assert_called_once()

    def test_setup_command(self):
        test_args = ["ai-usage", "setup"]
        with patch.object(sys, "argv", test_args):
            with patch("cli.ai_usage_cli.main.cmd_setup") as mock:
                main()
                mock.assert_called_once()

    def test_reset_command(self):
        test_args = ["ai-usage", "reset"]
        with patch.object(sys, "argv", test_args):
            with patch("cli.ai_usage_cli.main.cmd_reset") as mock:
                main()
                mock.assert_called_once()

    def test_help_flag(self):
        test_args = ["ai-usage", "--help"]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call("AI Usage Widget")

    def test_unknown_command(self):
        test_args = ["ai-usage", "unknown"]
        with patch.object(sys, "argv", test_args):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_any_call("Comando desconocido: unknown")


class TestCmdFunctions:
    @patch("cli.ai_usage_cli.main.opencode")
    @patch("cli.ai_usage_cli.main.chatgpt")
    @patch("cli.ai_usage_cli.main.show_status")
    def test_cmd_status(self, mock_show, mock_chatgpt, mock_opencode):
        mock_opencode.get_usage.return_value = {"provider": "opencode_go"}
        mock_chatgpt.get_usage.return_value = {"provider": "chatgpt"}
        cmd_status()
        mock_show.assert_called_once_with(
            {
                "opencode_go": {"provider": "opencode_go"},
                "chatgpt": {"provider": "chatgpt"},
            }
        )

    @patch("cli.ai_usage_cli.main.opencode")
    @patch("cli.ai_usage_cli.main.show_models")
    def test_cmd_models(self, mock_show, mock_opencode):
        mock_opencode.get_usage.return_value = {"provider": "opencode_go"}
        cmd_models()
        mock_show.assert_called_once_with(
            {
                "opencode_go": {"provider": "opencode_go"},
            }
        )

    @patch("scraper.opencode_go.fetch_go_usage")
    @patch("scraper.cookies.save_cookies")
    @patch("scraper.cookies.cookies_to_header")
    @patch("cli.ai_usage_cli.main._try_auto_cookies")
    @patch("core.ai_usage_widget.config.set_subscription_start")
    def test_cmd_setup_auto(
        self,
        mock_set_sub,
        mock_auto,
        mock_header,
        mock_save,
        mock_fetch,
        capsys,
    ):
        mock_auto.return_value = [{"name": "session", "value": "abc"}]
        mock_header.return_value = "session=abc"
        mock_fetch.return_value = MagicMock(
            five_hour_pct=30,
            five_hour_reset_seconds=5000,
            weekly_pct=50,
            weekly_reset_seconds=200000,
            monthly_pct=10,
            monthly_reset_seconds=500000,
        )
        with patch("scraper.cookies.save_cookie_entries") as mock_save_entries:
            cmd_setup()
            mock_save_entries.assert_called_once()

    @patch("scraper.cookies.clear_cookies")
    @patch("core.ai_usage_widget.config.set_subscription_start")
    def test_cmd_reset(self, mock_set_sub, mock_clear, capsys):
        cmd_reset()
        mock_clear.assert_called_once()
        mock_set_sub.assert_called_once_with(0)
