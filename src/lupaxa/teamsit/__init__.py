"""lupaxa.teamsit — send Microsoft Teams messages through an incoming webhook."""

from __future__ import annotations

from .client import DEFAULT_COLOR, DEFAULT_TIMEOUT, WEBHOOK_PREFIX, Teamsit
from .config import ConfigError, Profile, default_config_path, load_profile
from .version import __version__, get_version

__all__ = [
    "DEFAULT_COLOR",
    "DEFAULT_TIMEOUT",
    "WEBHOOK_PREFIX",
    "ConfigError",
    "Profile",
    "Teamsit",
    "__version__",
    "default_config_path",
    "get_version",
    "load_profile",
]
