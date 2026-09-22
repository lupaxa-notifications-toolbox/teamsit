"""Command-line interface for Teamsit."""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

import requests

from .client import DEFAULT_TIMEOUT, Teamsit, normalize_color
from .config import ConfigError, resolve_settings
from .version import get_version


def _positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be greater than 0")
    return timeout


def _color(value: str) -> str:
    try:
        return normalize_color(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _exit_code(exc: SystemExit) -> int:
    code = exc.code
    if code is None:
        return 0
    return code if isinstance(code, int) else 1


def _program_name(argv0: str) -> str:
    name = os.path.basename(argv0)
    return "teamsit" if name == "__main__.py" else name


def build_parser() -> argparse.ArgumentParser:
    """Build the ``teamsit`` argument parser."""
    parser = argparse.ArgumentParser(
        description="Send a Microsoft Teams message through an incoming webhook.",
    )
    parser.add_argument(
        "-w",
        "--webhook",
        default=None,
        metavar="URL",
        help="Teams incoming webhook URL (overrides the profile)",
    )
    parser.add_argument(
        "-p",
        "--profile",
        default=None,
        metavar="NAME",
        help="Profile name in the config file",
    )
    parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help="Config file (default: ~/.teamsit.yml)",
    )
    parser.add_argument("--title", default=None, help="Card title")
    parser.add_argument(
        "--color",
        type=_color,
        default=None,
        metavar="HEX",
        help="Theme color as 6-digit hex (default: 00FF00)",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        type=_positive_timeout,
        default=None,
        metavar="SECONDS",
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT:g})",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-t", "--text", help="Message text")
    mode.add_argument("--card", help="MessageCard JSON object")
    mode.add_argument(
        "--validate",
        action="store_true",
        help="Send a validation message",
    )
    parser.add_argument("--version", action="version", version=get_version())
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return _exit_code(exc)

    config_path = Path(args.config).expanduser() if args.config else None
    try:
        settings = resolve_settings(
            profile_name=args.profile,
            config_path=config_path,
            webhook_url=args.webhook,
            title=args.title,
            color=args.color,
            timeout=args.timeout,
        )
        client = Teamsit(
            settings.webhook_url,
            title=settings.title,
            color=settings.color,
            timeout=settings.timeout,
        )
        if args.validate:
            if not client.validate():
                print(f"{_program_name(sys.argv[0])}: invalid webhook URL", file=sys.stderr)
                return 1
            return 0
        if args.text is not None:
            client.send_message(args.text)
        elif args.card is not None:
            client.send_card(args.card)
    except ConfigError as exc:
        print(f"{_program_name(sys.argv[0])}: {exc}", file=sys.stderr)
        return 2
    except (ValueError, requests.RequestException) as exc:
        print(f"{_program_name(sys.argv[0])}: {exc}", file=sys.stderr)
        return 1
    return 0
