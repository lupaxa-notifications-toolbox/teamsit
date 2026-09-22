<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-notifications-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/notifications-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa Notifications Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-teamsit

Send Microsoft Teams messages through an incoming webhook.

## Features

- Post message text as an Office 365 MessageCard, or send a card JSON object
- Set a title and theme color on each client
- Keep several webhook profiles in `$HOME/.teamsit.yml` and select one with `--profile`
- Override any profile field with a CLI flag
- Turn escaped `\n` sequences in message text into real line breaks
- Accept Office 365 connector URLs and `*.webhook.office.com/webhookb2/` addresses
- Reject webhook URLs that answer `HEAD` with a redirect
- Use the `Teamsit` library class or the `teamsit` command

## Installation

### From PyPI

```bash
pip install lupaxa-teamsit
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

Requires Python 3.13+. Runtime dependencies: `requests` and `PyYAML`.

## Library quick start

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
)
client.send_message("Hello, Teams!")
client.send_card('{"summary": "Custom card", "text": "Body"}')
```

## CLI quick start

```bash
teamsit --help
teamsit --webhook "$TEAMS_WEBHOOK_URL" --text "Hello, Teams!"
teamsit --profile testing --text "Hello, Teams!"
teamsit -p alerts --config "$HOME/work/teamsit.yml" --text "Disk full"
```

You can also run the CLI as a module:

```bash
python -m lupaxa.teamsit --help
python -m lupaxa.teamsit --version
```

## Config

Profiles live in one YAML file. The default path is `$HOME/.teamsit.yml`.
Pass `--config` when the file lives somewhere else. `--config` requires
`--profile`. CLI flags override the selected profile.

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
`--webhook` is required when you do not pass `--profile`.

## Options

- `--webhook`, `-w`: Teams incoming webhook URL; required when `--profile` is omitted
- `--profile`, `-p`: profile name in the config file
- `--config`: config file path; default `$HOME/.teamsit.yml`
- `--text`, `-t`: message text
- `--card`: one MessageCard as a JSON object
- `--validate`: send a validation message
- `--title`: card title
- `--color`: theme color as 6-digit hex; default `00FF00`
- `--timeout`, `-T`: request timeout in seconds; default `10`
- `--version`: print the package version

`--text`, `--card`, and `--validate` are mutually exclusive.
One of them is required. CLI flags override the selected profile.

## Documentation

Online documentation:

[Documentation](https://teamsit.thelupaxaproject.org/)

Source repository:

[GitHub](https://github.com/lupaxa-notifications-toolbox/teamsit)

### Serve docs locally

From a clone of the repository:

```bash
make mkdocs-serve
```

Then open the local URL printed by MkDocs in your browser.

## Development

Clone the repository and install with Make:

```bash
make init                # first-time makefile-skills checkout
make python-install-dev  # editable install with [dev]
make python-check        # lint, type-check, and test
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
