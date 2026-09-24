# Teamsit

`lupaxa-teamsit` posts messages to Microsoft Teams through an incoming webhook.
Use it as a library or as the `teamsit` command.

```bash
pip install lupaxa-teamsit
teamsit --webhook "$TEAMS_WEBHOOK_URL" --text "Hello, Teams!"
teamsit --profile testing --text "Hello, Teams!"
```

A successful post returns when Teams answers HTTP 200. The webhook URL must be
an Office 365 connector address or a `*.webhook.office.com/webhookb2/` address.
`--profile` reads a named profile from `$HOME/.teamsit.yml`.
