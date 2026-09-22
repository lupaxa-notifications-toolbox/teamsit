"""CLI entrypoint."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lupaxa.teamsit.cli import _program_name, build_parser, main
from lupaxa.teamsit.version import get_version

WEBHOOK = "https://outlook.office.com/webhook/YOUR_WEBHOOK_URL"
_BASE = ["--webhook", WEBHOOK]


def test_help_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--help"]) == 0
    assert "--webhook" in capsys.readouterr().out


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--version"]) == 0
    assert get_version() in capsys.readouterr().out


def test_missing_webhook_exits_two(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--text", "hi"]) == 2
    assert "webhook URL required" in capsys.readouterr().err


def test_missing_mode_exits_two() -> None:
    assert main(_BASE) == 2


def test_parser_defaults() -> None:
    args = build_parser().parse_args([*_BASE, "--text", "hi"])
    assert args.webhook == WEBHOOK
    assert args.text == "hi"
    assert args.timeout is None
    assert args.profile is None
    assert args.title is None
    assert args.color is None
    overridden = build_parser().parse_args(
        [*_BASE, "--text", "hi", "--timeout", "2.5", "--color", "#00ff00"]
    )
    assert overridden.timeout == 2.5
    assert overridden.color == "00FF00"


def test_timeout_must_be_a_number() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_BASE, "--text", "hi", "--timeout", "nope"])


def test_color_must_be_hex() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_BASE, "--text", "hi", "--color", "green"])


def test_text_calls_send_message() -> None:
    client = MagicMock()
    with patch("lupaxa.teamsit.cli.Teamsit", return_value=client) as ctor:
        assert main([*_BASE, "--title", "Deploy", "--color", "0078D4", "--text", "hi"]) == 0
    ctor.assert_called_once_with(
        WEBHOOK,
        title="Deploy",
        color="0078D4",
        timeout=10.0,
    )
    client.send_message.assert_called_once_with("hi")


def test_card() -> None:
    client = MagicMock()
    with patch("lupaxa.teamsit.cli.Teamsit", return_value=client):
        assert main([*_BASE, "--card", "{}"]) == 0
    client.send_card.assert_called_once_with("{}")


def test_profile_fills_client_and_flags_override(tmp_path: Path) -> None:
    path = tmp_path / "teamsit.yml"
    path.write_text(
        "\n".join(
            [
                "profiles:",
                "  testing:",
                f"    webhook_url: {WEBHOOK}",
                "    title: Alerts",
                "    color: FF0000",
                "    timeout: 15",
            ],
        ),
        encoding="utf-8",
    )
    client = MagicMock()
    with patch("lupaxa.teamsit.cli.Teamsit", return_value=client) as ctor:
        assert (
            main(
                [
                    "-p",
                    "testing",
                    "--config",
                    str(path),
                    "--title",
                    "Other",
                    "--text",
                    "hi",
                ]
            )
            == 0
        )
    ctor.assert_called_once_with(
        WEBHOOK,
        title="Other",
        color="FF0000",
        timeout=15.0,
    )


def test_unknown_profile_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "teamsit.yml"
    path.write_text(
        f"profiles:\n  testing:\n    webhook_url: {WEBHOOK}\n",
        encoding="utf-8",
    )
    assert main(["-p", "missing", "--config", str(path), "--text", "hi"]) == 2
    assert "profile not found" in capsys.readouterr().err


def test_validate_success_and_failure() -> None:
    client = MagicMock()
    client.validate.return_value = True
    with patch("lupaxa.teamsit.cli.Teamsit", return_value=client):
        assert main([*_BASE, "--validate"]) == 0
    client.validate.return_value = False
    with patch("lupaxa.teamsit.cli.Teamsit", return_value=client):
        assert main([*_BASE, "--validate"]) == 1


def test_value_error_uses_program_prefix(capsys: pytest.CaptureFixture[str]) -> None:
    with (
        patch("lupaxa.teamsit.cli.Teamsit", side_effect=ValueError("bad webhook")),
        patch("lupaxa.teamsit.cli.sys.argv", ["/path/to/teamsit"]),
    ):
        assert main([*_BASE, "--text", "hi"]) == 1
    assert capsys.readouterr().err == "teamsit: bad webhook\n"


@pytest.mark.parametrize(
    ("argv0", "expected"),
    [
        ("/path/to/teamsit", "teamsit"),
        ("/path/to/__main__.py", "teamsit"),
    ],
)
def test_program_name(argv0: str, expected: str) -> None:
    assert _program_name(argv0) == expected


def test_timeout_flag_rejected() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_BASE, "--text", "hi", "--timeout", "0"])
