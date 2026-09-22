# Usage

Use `teamsit` to post one message or one MessageCard.
Pass the webhook URL with `--webhook`, or select a profile with `--profile`.

## CLI flags

| Flag              | Default          | Description                                |
| :---------------- | :--------------- | :----------------------------------------- |
| `--webhook`, `-w` | profile value    | Microsoft Teams incoming webhook URL       |
| `--profile`, `-p` | —                | Profile name in the config file            |
| `--config`        | `~/.teamsit.yml` | Config file path                           |
| `--text`, `-t`    | —                | Message text                               |
| `--title`         | profile value    | Card title                                 |
| `--color`         | `00FF00`         | Theme color as 6-digit hex                 |
| `--card`          | —                | MessageCard JSON object                    |
| `--validate`      | —                | Send a validation message                  |
| `--timeout`, `-T` | `10`             | Request timeout in seconds                 |
| `--version`       | —                | Print the package version and exit         |

```bash
teamsit --webhook "$TEAMS_WEBHOOK_URL" --title Deploy --color 0078D4 --text "Hello"
```

`--text`, `--card`, and `--validate` are mutually exclusive.
One of them is required. `--timeout` must be greater than `0`. A flag overrides
the same field from the selected profile.

## Config file

Profiles live in one YAML file. The default path is `$HOME/.teamsit.yml`.
Pass `--config` when the file lives somewhere else.

```yaml
profiles:
  testing:
    webhook_url: https://outlook.office.com/webhook/YOUR_WEBHOOK_URL
    title: Alerts
    color: "00FF00"
    timeout: 15
  notices:
    webhook_url: https://contoso.webhook.office.com/webhookb2/YOUR_WEBHOOK_URL
    title: Notice
```

```bash
teamsit --profile testing --text "Hello"
teamsit -p notices --config "$HOME/work/teamsit.yml" --text "Disk full"
```

Each profile may set `webhook_url`, `title`, `color`, and `timeout`. Other
keys are rejected. `--webhook` is still required when you do not pass
`--profile`. `--config` requires `--profile`.

Escaped newlines in `--text` are sent as real line breaks, so `Hello\\nthere`
arrives as two lines. The text is posted as an Office 365 MessageCard:
`summary` and `activityTitle` use `--title` when it is set, and `themeColor`
uses `--color`.

## Library

```python
from lupaxa.teamsit import Teamsit, load_profile

profile = load_profile("testing")
client = Teamsit(
    profile.webhook_url,
    title=profile.title,
    color=profile.color or "00FF00",
)
client.send_message("Hello from a profile")

client = Teamsit(
    "https://outlook.office.com/webhook/YOUR_WEBHOOK_URL",
    title="Deploy",
    color="0078D4",
    timeout=10.0,
)
client.send_message("Hello, Teams!")
client.send("Hello, Teams!")
client.send_card('{"summary": "Custom card", "text": "Body"}')
```

`JsonValue` is a JSON string, number, boolean, null, list, or object. `send`
is an alias of `send_message`. A card posted with `send_card` or
`send_payload` receives `@type`, `@context`, and `themeColor` when those
fields are absent. `validate` checks the webhook again and posts
`This is a validation message`.

Signatures:

```python
Teamsit(
    webhook_url: str,
    *,
    title: str | None = None,
    color: str = "00FF00",
    timeout: float = 10.0,
)

send_message(text: str) -> bool
send(text: str) -> bool
send_card(card: str) -> bool
send_payload(payload: dict[str, JsonValue]) -> bool
validate() -> bool

load_profile(name: str, path: Path | None = None) -> Profile
```

`load_profile` reads `$HOME/.teamsit.yml` when `path` is omitted. A missing
file, unknown profile, or invalid YAML raises `ConfigError`.
