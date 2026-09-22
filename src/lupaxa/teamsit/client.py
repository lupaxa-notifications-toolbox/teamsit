"""Microsoft Teams incoming-webhook client."""

from __future__ import annotations

import json
import math
import re
from typing import cast

import requests

DEFAULT_TIMEOUT = 10.0
DEFAULT_COLOR = "00FF00"
WEBHOOK_PREFIX = "https://outlook.office.com/webhook/"
_OFFICE365_PREFIX = "https://outlook.office365.com/webhook/"
_MESSAGE_CARD = "MessageCard"
_CARD_CONTEXT = "http://schema.org/extensions"
_REDIRECT_STATUSES = {301, 302}
_COLOR = re.compile(r"^#?([0-9A-Fa-f]{6})$")

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]


def is_teams_webhook(url: str) -> bool:
    """Return whether ``url`` is an Office 365 connector or Teams webhook address."""
    if url.startswith((WEBHOOK_PREFIX, _OFFICE365_PREFIX)):
        return True
    if not url.startswith("https://"):
        return False
    host, separator, path = url.removeprefix("https://").partition("/")
    return (
        bool(separator) and host.endswith(".webhook.office.com") and path.startswith("webhookb2/")
    )


def normalize_color(value: object) -> str:
    """Return a 6-digit hex color without a leading ``#``."""
    if not isinstance(value, str):
        raise ValueError("color must be a 6-digit hex value")
    match = _COLOR.fullmatch(value.strip())
    if match is None:
        raise ValueError("color must be a 6-digit hex value")
    return match.group(1).upper()


class Teamsit:
    """Send messages through a Microsoft Teams incoming webhook."""

    def __init__(
        self,
        webhook_url: str,
        *,
        title: str | None = None,
        color: str = DEFAULT_COLOR,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Store webhook settings after the URL passes validation."""
        if not webhook_url:
            raise ValueError("Webhook URL required")
        if not is_teams_webhook(webhook_url):
            raise ValueError(
                f"Invalid webhook URL: {webhook_url} - should start with {WEBHOOK_PREFIX}"
                " or use a .webhook.office.com/webhookb2/ address"
            )
        self.webhook_url = webhook_url
        self.title = None if title is None else _require_text(title, "title")
        self.color = normalize_color(color)
        self.timeout = _require_timeout(timeout)
        if not self.valid_webhook(self.webhook_url):
            raise ValueError(
                f"Invalid webhook URL: {self.webhook_url} - please check your configuration"
            )

    def valid_webhook(self, url: str) -> bool:
        """Return whether ``url`` answers without a redirect."""
        try:
            response = requests.head(
                url,
                allow_redirects=False,
                timeout=self.timeout,
            )
        except requests.RequestException:
            return False
        return response.status_code not in _REDIRECT_STATUSES

    def send_message(self, text: str) -> bool:
        """Post ``text`` as a MessageCard, turning escaped newlines into line breaks."""
        summary = self.title if self.title else "Message"
        activity = self.title if self.title else "Notification"
        return self.send_payload(
            {
                "@type": _MESSAGE_CARD,
                "@context": _CARD_CONTEXT,
                "themeColor": self.color,
                "summary": summary,
                "sections": [
                    {
                        "activityTitle": activity,
                        "text": text.replace("\\n", "\n"),
                    }
                ],
            }
        )

    def send(self, text: str) -> bool:
        """Post ``text``. Alias of ``send_message``."""
        return self.send_message(text)

    def send_card(self, card: str) -> bool:
        """Post one MessageCard encoded as a JSON object string."""
        parsed = self.convert_to_json(card)
        if not isinstance(parsed, dict):
            raise ValueError("card must be a JSON object")
        return self.send_payload(parsed)

    def convert_to_json(self, json_string: str) -> JsonValue:
        """Parse ``json_string`` or raise ``ValueError``."""
        try:
            parsed = json.loads(json_string)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid json") from exc
        return cast(JsonValue, parsed)

    def send_payload(self, payload: dict[str, JsonValue]) -> bool:
        """POST ``payload`` as JSON, filling card type and theme color."""
        body = _with_defaults(payload, self.color)
        response = requests.post(
            self.webhook_url,
            headers={"Content-Type": "application/json"},
            json=body,
            timeout=self.timeout,
            allow_redirects=False,
        )
        if response.status_code == 200:
            return True
        if response.status_code in _REDIRECT_STATUSES:
            raise ValueError(
                f"Invalid webhook URL: {self.webhook_url} - please check your configuration"
            )
        if not response.text:
            raise ValueError(f"Unknown error for webhook URL: {self.webhook_url}")
        raise ValueError(response.text)

    def validate(self) -> bool:
        """Send a validation message when HEAD succeeds."""
        if not self.valid_webhook(self.webhook_url):
            return False
        self.send_message("This is a validation message")
        return True


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _require_timeout(timeout: float) -> float:
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("timeout must be a number")
    number = float(timeout)
    if not math.isfinite(number) or number <= 0:
        raise ValueError("timeout must be greater than 0")
    return number


def _with_defaults(payload: dict[str, JsonValue], color: str) -> dict[str, JsonValue]:
    body = dict(payload)
    if "@type" not in body:
        body["@type"] = _MESSAGE_CARD
    if "@context" not in body:
        body["@context"] = _CARD_CONTEXT
    if "themeColor" not in body:
        body["themeColor"] = color
    return body
