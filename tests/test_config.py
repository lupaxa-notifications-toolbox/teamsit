"""YAML profile config."""

from __future__ import annotations

from pathlib import Path

import pytest

from lupaxa.teamsit.config import (
    ConfigError,
    default_config_path,
    load_profile,
    resolve_settings,
)

WEBHOOK = "https://outlook.office.com/webhook/YOUR_WEBHOOK_URL"
OTHER = "https://contoso.webhook.office.com/webhookb2/YOUR_WEBHOOK_URL"

_FILE = f"""
profiles:
  testing:
    webhook_url: {WEBHOOK}
    title: Alerts
    color: "#ff0000"
    timeout: 15
  notices:
    webhook_url: {OTHER}
    title: Notice
"""


def test_default_config_path_is_home_dotfile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert default_config_path() == tmp_path / ".teamsit.yml"


def test_load_profile_uses_home_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    (tmp_path / ".teamsit.yml").write_text(_FILE, encoding="utf-8")
    assert load_profile("testing").webhook_url == WEBHOOK


def test_load_profile(tmp_path: Path) -> None:
    path = tmp_path / ".teamsit.yml"
    path.write_text(_FILE, encoding="utf-8")
    profile = load_profile("testing", path)
    assert profile.webhook_url == WEBHOOK
    assert profile.title == "Alerts"
    assert profile.color == "FF0000"
    assert profile.timeout == 15.0
    notices = load_profile("notices", path)
    assert notices.color is None
    assert notices.timeout is None


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="config file not found"):
        load_profile("testing", tmp_path / "missing.yml")


def test_unknown_profile(tmp_path: Path) -> None:
    path = tmp_path / ".teamsit.yml"
    path.write_text(_FILE, encoding="utf-8")
    with pytest.raises(ConfigError, match="profile not found: missing"):
        load_profile("missing", path)


def test_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / ".teamsit.yml"
    path.write_text("profiles: [\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="invalid config file"):
        load_profile("testing", path)


def test_unknown_setting(tmp_path: Path) -> None:
    path = tmp_path / ".teamsit.yml"
    path.write_text(
        f"profiles:\n  testing:\n    webhook_url: {WEBHOOK}\n    token: secret\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="unknown profile setting: token"):
        load_profile("testing", path)


def test_resolve_profile_and_cli_override(tmp_path: Path) -> None:
    path = tmp_path / ".teamsit.yml"
    path.write_text(_FILE, encoding="utf-8")
    settings = resolve_settings(
        profile_name="testing",
        config_path=path,
        webhook_url=None,
        title="Other",
        color=None,
        timeout=None,
    )
    assert settings.webhook_url == WEBHOOK
    assert settings.title == "Other"
    assert settings.color == "FF0000"
    assert settings.timeout == 15.0


def test_resolve_without_profile_uses_defaults() -> None:
    settings = resolve_settings(
        profile_name=None,
        config_path=None,
        webhook_url=WEBHOOK,
        title=None,
        color=None,
        timeout=None,
    )
    assert settings.timeout == 10.0
    assert settings.color == "00FF00"
    assert settings.title is None


def test_config_without_profile_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="--profile is required"):
        resolve_settings(
            profile_name=None,
            config_path=tmp_path / ".teamsit.yml",
            webhook_url=WEBHOOK,
            title=None,
            color=None,
            timeout=None,
        )


def test_cli_timeout_overrides_profile(tmp_path: Path) -> None:
    path = tmp_path / ".teamsit.yml"
    path.write_text(_FILE, encoding="utf-8")
    settings = resolve_settings(
        profile_name="testing",
        config_path=path,
        webhook_url=OTHER,
        title=None,
        color="00ff00",
        timeout=3,
    )
    assert settings.webhook_url == OTHER
    assert settings.title == "Alerts"
    assert settings.color == "00FF00"
    assert settings.timeout == 3


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("profiles: {}\n", "must define profiles"),
        ("note: hi\nprofiles:\n  testing:\n    webhook_url: x\n", "unknown config setting"),
        ("[]\n", "invalid config file"),
        (
            "profiles:\n  testing:\n    webhook_url: x\n    timeout: 0\n",
            "timeout must be greater than 0",
        ),
        (
            'profiles:\n  testing:\n    webhook_url: ""\n',
            "webhook_url must be a non-empty string",
        ),
        (
            "profiles:\n  testing:\n    webhook_url: x\n    color: green\n",
            "color must be a 6-digit hex value",
        ),
    ],
)
def test_rejected_config_shapes(tmp_path: Path, text: str, match: str) -> None:
    path = tmp_path / ".teamsit.yml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match=match):
        load_profile("testing", path)


def test_missing_webhook_is_rejected() -> None:
    with pytest.raises(ConfigError, match="webhook URL required"):
        resolve_settings(
            profile_name=None,
            config_path=None,
            webhook_url=None,
            title=None,
            color=None,
            timeout=None,
        )
