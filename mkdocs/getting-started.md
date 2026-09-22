# Getting started

## Requirements

- Python 3.13 or newer
- A Microsoft Teams incoming webhook URL you are allowed to post to
- `requests` and `PyYAML`, installed with the package

## Install

```bash
pip install lupaxa-teamsit
teamsit --help
```

## First run

```bash
teamsit --webhook "$TEAMS_WEBHOOK_URL" --title "Deploy" --text "Hello, Teams!"
```

The command exits `0` when Teams accepts the message. Put the webhook URL in
the environment, or in a profile, rather than in shell history.

## Config file

Profiles live in `$HOME/.teamsit.yml`. Pass `--config` when the file lives
somewhere else. `--config` requires `--profile`.

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
teamsit --profile testing --text "Hello, Teams!"
teamsit -p notices --config "$HOME/work/teamsit.yml" --text "Disk full"
```

Each profile may set `webhook_url`, `title`, `color`, and `timeout`. A CLI
flag overrides the same field from the profile.

Module entry point:

```bash
python -m lupaxa.teamsit --version
```

### From source (development)

```bash
make init
make python-install-dev
teamsit --version
```

## Makefile helpers

```bash
make init                 # clone makefile-skills into .makefiles/
make python-install-dev   # editable install with [dev]
make python-check         # lint + type + test
make mkdocs-serve         # local docs site
```
