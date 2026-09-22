"""Teamsit client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from lupaxa.teamsit.client import WEBHOOK_PREFIX, Teamsit, is_teams_webhook, normalize_color

WEBHOOK = f"{WEBHOOK_PREFIX}YOUR_WEBHOOK_URL"
OFFICE = "https://contoso.webhook.office.com/webhookb2/YOUR_WEBHOOK_URL"


def _response(status: int, text: str = "ok") -> MagicMock:
    response = MagicMock()
    response.status_code = status
    response.text = text
    return response


def _client(**kwargs: object) -> Teamsit:
    with patch("lupaxa.teamsit.client.requests.head", return_value=_response(200)):
        return Teamsit(WEBHOOK, **kwargs)  # type: ignore[arg-type]


def test_missing_webhook_raises() -> None:
    with pytest.raises(ValueError, match="Webhook URL required"):
        Teamsit("")


def test_prefix_is_required() -> None:
    with pytest.raises(ValueError, match="should start with"):
        Teamsit("https://example.com/hook")


@pytest.mark.parametrize(
    "url",
    [
        WEBHOOK,
        "https://outlook.office365.com/webhook/YOUR_WEBHOOK_URL",
        OFFICE,
    ],
)
def test_accepted_webhook_shapes(url: str) -> None:
    assert is_teams_webhook(url) is True
    with patch("lupaxa.teamsit.client.requests.head", return_value=_response(200)):
        assert Teamsit(url).webhook_url == url


def test_redirect_on_head_is_rejected() -> None:
    with (
        patch("lupaxa.teamsit.client.requests.head", return_value=_response(302)),
        pytest.raises(ValueError, match="please check your configuration"),
    ):
        Teamsit(WEBHOOK)


def test_head_error_is_rejected() -> None:
    with (
        patch(
            "lupaxa.teamsit.client.requests.head",
            side_effect=requests.ConnectionError("down"),
        ),
        pytest.raises(ValueError, match="please check your configuration"),
    ):
        Teamsit(WEBHOOK)


def test_send_message_posts_card_defaults() -> None:
    client = _client()
    with patch(
        "lupaxa.teamsit.client.requests.post",
        return_value=_response(200),
    ) as post:
        assert client.send_message("Hello\\nthere") is True
    body = post.call_args.kwargs["json"]
    assert body["@type"] == "MessageCard"
    assert body["@context"] == "http://schema.org/extensions"
    assert body["themeColor"] == "00FF00"
    assert body["summary"] == "Message"
    assert body["sections"] == [{"activityTitle": "Notification", "text": "Hello\nthere"}]
    assert post.call_args.kwargs["allow_redirects"] is False
    assert post.call_args.kwargs["headers"]["Content-Type"] == "application/json"


def test_send_message_uses_title_and_color() -> None:
    client = _client(title="Deploy", color="#00ff00")
    with patch(
        "lupaxa.teamsit.client.requests.post",
        return_value=_response(200),
    ) as post:
        client.send_message("shipped")
    body = post.call_args.kwargs["json"]
    assert body["themeColor"] == "00FF00"
    assert body["summary"] == "Deploy"
    assert body["sections"][0]["activityTitle"] == "Deploy"


def test_send_is_alias() -> None:
    client = _client()
    with patch.object(client, "send_message", return_value=True) as send_message:
        assert client.send("hi") is True
    send_message.assert_called_once_with("hi")


def test_send_card() -> None:
    client = _client(color="112233")
    with patch(
        "lupaxa.teamsit.client.requests.post",
        return_value=_response(200),
    ) as post:
        assert client.send_card('{"summary": "Custom"}') is True
    body = post.call_args.kwargs["json"]
    assert body["summary"] == "Custom"
    assert body["@type"] == "MessageCard"
    assert body["themeColor"] == "112233"


def test_invalid_json_raises() -> None:
    client = _client()
    with pytest.raises(ValueError, match="Invalid json"):
        client.send_card("not-json")


def test_card_must_be_object() -> None:
    client = _client()
    with pytest.raises(ValueError, match="card must be a JSON object"):
        client.send_card("[]")


def test_payload_color_wins_over_default() -> None:
    client = _client(color="00FF00")
    with patch(
        "lupaxa.teamsit.client.requests.post",
        return_value=_response(200),
    ) as post:
        client.send_payload({"summary": "hi", "themeColor": "ABCDEF"})
    assert post.call_args.kwargs["json"]["themeColor"] == "ABCDEF"


@pytest.mark.parametrize(
    ("status", "text", "match"),
    [
        (302, "", "please check your configuration"),
        (500, "", "Unknown error"),
        (400, "invalid_payload", "invalid_payload"),
    ],
)
def test_post_errors(status: int, text: str, match: str) -> None:
    client = _client()
    with (
        patch(
            "lupaxa.teamsit.client.requests.post",
            return_value=_response(status, text),
        ),
        pytest.raises(ValueError, match=match),
    ):
        client.send_message("hi")


def test_request_exception_propagates() -> None:
    client = _client()
    with (
        patch(
            "lupaxa.teamsit.client.requests.post",
            side_effect=requests.Timeout("slow"),
        ),
        pytest.raises(requests.Timeout),
    ):
        client.send_message("hi")


def test_validate_sends_message() -> None:
    client = _client(title="Alerts")
    with (
        patch("lupaxa.teamsit.client.requests.head", return_value=_response(200)),
        patch(
            "lupaxa.teamsit.client.requests.post",
            return_value=_response(200),
        ) as post,
    ):
        assert client.validate() is True
    body = post.call_args.kwargs["json"]
    assert body["sections"][0]["text"] == "This is a validation message"
    assert body["summary"] == "Alerts"


def test_validate_false_when_head_fails() -> None:
    client = _client()
    with patch.object(client, "valid_webhook", return_value=False):
        assert client.validate() is False


def test_timeout_must_be_positive() -> None:
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        _client(timeout=0)


def test_color_must_be_hex() -> None:
    with pytest.raises(ValueError, match="6-digit hex"):
        _client(color="green")


def test_normalize_color() -> None:
    assert normalize_color("  #00ff00 ") == "00FF00"


def test_blank_title_rejected() -> None:
    with pytest.raises(ValueError, match="title must be a non-empty string"):
        _client(title="  ")
