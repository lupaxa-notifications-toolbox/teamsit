<p align="center">
  <a href="https://github.com/lupaxa-notifications-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/notifications-toolbox/readme-logo.png" alt="Notifications Toolbox" />
  </a>
</p>

<h1 align="center">Teamsit</h1>

Send Microsoft Teams messages through an incoming webhook.

Requires Python 3.13 or newer. A successful post returns when Teams answers
HTTP 200.

## Install

```bash
pip install lupaxa-teamsit
teamsit --help
```

## CLI

```bash
teamsit --webhook "$TEAMS_WEBHOOK_URL" --text "Hello, Teams!"
teamsit --webhook "$TEAMS_WEBHOOK_URL" --title Deploy --color 0078D4 --text "Hello"
teamsit --profile testing --text "Hello, Teams!"
teamsit -p alerts --config "$HOME/work/teamsit.yml" --text "Disk full"
teamsit --webhook "$TEAMS_WEBHOOK_URL" --validate
python -m lupaxa.teamsit --version
```

The webhook URL must be an Office 365 connector address
(`https://outlook.office.com/webhook/…` or
`https://outlook.office365.com/webhook/…`) or a Teams incoming webhook
(`https://….webhook.office.com/webhookb2/…`).
`--text`, `--card`, and `--validate` are mutually exclusive, and one of them
is required. Flags override the same fields from the selected profile.

| Flag              | Default          | Description                          |
| :---------------- | :--------------- | :----------------------------------- |
| `--webhook`, `-w` | profile value    | Microsoft Teams incoming webhook URL |
| `--profile`, `-p` | —                | Profile name in the config file      |
| `--config`        | `~/.teamsit.yml` | Config file path                     |
| `--text`, `-t`    | —                | Message text                         |
| `--title`         | profile value    | Card title                           |
| `--color`         | `00FF00`         | Theme color as 6-digit hex           |
| `--card`          | —                | MessageCard JSON object              |
| `--validate`      | —                | Send a validation message            |
| `--timeout`, `-T` | `10`             | Request timeout in seconds           |
| `--version`       | —                | Print the package version and exit   |

`--timeout` must be greater than `0`. `--color` is six hex digits, with or
without a leading `#`. Escaped newlines in `--text` are sent as real line
breaks, so `Hello\\nthere` arrives as two lines. The text is posted as an
Office 365 MessageCard: `summary` and `activityTitle` use `--title` when it
is set, and `themeColor` uses `--color`. `--validate` posts
`This is a validation message`.

| Code | When                                                         |
| :--- | :----------------------------------------------------------- |
| `0`  | Help, version, or Teams accepted the post                    |
| `1`  | The webhook was rejected, or the post failed                 |
| `2`  | Command-line usage, a bad config, or argument parsing failed |

## Config

Profiles live in `$HOME/.teamsit.yml`. Pass `--config` to use another file.
`--config` requires `--profile`.

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

Each profile may set `webhook_url`, `title`, `color`, and `timeout`. Other
keys are rejected. `--webhook` is required when you do not pass `--profile`.

## Library

```python
from lupaxa.teamsit import Teamsit, load_profile

profile = load_profile("testing")
client = Teamsit(
    profile.webhook_url,
    title=profile.title,
    color=profile.color or "00FF00",
)
client.send_message("Hello, Teams!")
client.send("Hello\\nfrom the library")
client.send_card('{"summary": "Deploy finished", "text": "All jobs passed"}')
```

`send` is an alias of `send_message`. A card posted with `send_card` receives
`@type`, `@context`, and `themeColor` when those fields are absent.
`load_profile` reads `$HOME/.teamsit.yml` when no path is passed. A missing
file, unknown profile, or invalid YAML raises `ConfigError`.

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
