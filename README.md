<p align="center">
  <a href="https://github.com/lupaxa-notifications-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/notifications-toolbox/readme-logo.png" alt="Notifications Toolbox" />
  </a>
</p>

<h1 align="center">Teamsit</h1>

Send Microsoft Teams messages through an incoming webhook.

## Install

```bash
pip install lupaxa-teamsit
teamsit --help
```

## CLI

```bash
teamsit --webhook "$TEAMS_WEBHOOK_URL" --text "Hello, Teams!"
teamsit --profile testing --text "Hello, Teams!"
teamsit -p alerts --config "$HOME/work/teamsit.yml" --text "Disk full"
python -m lupaxa.teamsit --version
```

The webhook URL must be an Office 365 connector address
(`https://outlook.office.com/webhook/…`) or a Teams incoming webhook
(`https://….webhook.office.com/webhookb2/…`).
`--text`, `--card`, and `--validate` are mutually exclusive.
Flags override the same fields from the selected profile.

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

Each profile may set `webhook_url`, `title`, `color`, and `timeout`.

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
```

## Development

```bash
make init
make python-install-dev
make python-check
```

## Documentation

Site pages live in `mkdocs/` and publish to
<https://teamsit.thelupaxaproject.org/>.

```bash
make init
make python-install-dev
make mkdocs-serve
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
