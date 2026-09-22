"""Load Teamsit profiles from a YAML config file."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import yaml

from .client import DEFAULT_COLOR, DEFAULT_TIMEOUT, normalize_color

_PROFILE_FIELDS = ("webhook_url", "title", "color", "timeout")


class ConfigError(ValueError):
    """The config file or selected profile cannot be used."""


@dataclass(frozen=True)
class Profile:
    """One named block of webhook settings from the config file."""

    webhook_url: str | None = None
    title: str | None = None
    color: str | None = None
    timeout: float | None = None


@dataclass(frozen=True)
class ResolvedSettings:
    """Webhook settings after CLI flags override a profile."""

    webhook_url: str
    title: str | None
    color: str
    timeout: float


def default_config_path() -> Path:
    """Return the default config path, ``$HOME/.teamsit.yml``."""
    return Path.home() / ".teamsit.yml"


def load_profile(name: str, path: Path | None = None) -> Profile:
    """Load ``name`` from ``path`` or from ``$HOME/.teamsit.yml``."""
    config_path = default_config_path() if path is None else path
    if not config_path.is_file():
        raise ConfigError(f"config file not found: {config_path}")
    try:
        loaded: object = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid config file: {config_path}") from exc
    profiles = _profiles(loaded, config_path)
    if name not in profiles:
        raise ConfigError(f"profile not found: {name}")
    raw = profiles[name]
    if not isinstance(raw, dict):
        raise ConfigError(f"profile {name} must be a mapping")
    unknown = sorted(str(key) for key in raw if key not in _PROFILE_FIELDS)
    if unknown:
        raise ConfigError(f"unknown profile setting: {', '.join(unknown)}")
    return Profile(
        webhook_url=_optional_text(raw.get("webhook_url"), "webhook_url"),
        title=_optional_text(raw.get("title"), "title"),
        color=_optional_color(raw.get("color")),
        timeout=_optional_timeout(raw.get("timeout")),
    )


def resolve_settings(
    *,
    profile_name: str | None,
    config_path: Path | None,
    webhook_url: str | None,
    title: str | None,
    color: str | None,
    timeout: float | None,
) -> ResolvedSettings:
    """Merge CLI values over an optional profile.

    A passed CLI value wins. ``timeout`` falls back to ``DEFAULT_TIMEOUT``.
    ``color`` falls back to ``DEFAULT_COLOR``.
    """
    if profile_name is None and config_path is not None:
        raise ConfigError("--profile is required when --config is set")
    profile = load_profile(profile_name, config_path) if profile_name else None
    resolved_webhook = _pick(webhook_url, None if profile is None else profile.webhook_url)
    if not resolved_webhook:
        raise ConfigError("webhook URL required")
    if color is not None:
        resolved_color = normalize_color(color)
    elif profile is not None and profile.color is not None:
        resolved_color = profile.color
    else:
        resolved_color = DEFAULT_COLOR
    if timeout is not None:
        resolved_timeout = timeout
    elif profile is not None and profile.timeout is not None:
        resolved_timeout = profile.timeout
    else:
        resolved_timeout = DEFAULT_TIMEOUT
    return ResolvedSettings(
        webhook_url=resolved_webhook,
        title=_pick(title, None if profile is None else profile.title),
        color=resolved_color,
        timeout=resolved_timeout,
    )


def _pick(cli_value: str | None, profile_value: str | None) -> str | None:
    return cli_value if cli_value is not None else profile_value


def _profiles(loaded: object, config_path: Path) -> dict[object, object]:
    if not isinstance(loaded, dict):
        raise ConfigError(f"invalid config file: {config_path}")
    unknown = sorted(str(key) for key in loaded if key != "profiles")
    if unknown:
        raise ConfigError(f"unknown config setting: {', '.join(unknown)}")
    profiles = loaded.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ConfigError("config file must define profiles")
    for name in profiles:
        if not isinstance(name, str) or not name:
            raise ConfigError("profile names must be strings")
    return profiles


def _optional_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{field} must be a non-empty string")
    return value.strip()


def _optional_color(value: object) -> str | None:
    if value is None:
        return None
    try:
        return normalize_color(value)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc


def _optional_timeout(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError("timeout must be a number")
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ConfigError("timeout must be greater than 0")
    return timeout
