# Examples

## Plain Text

```bash
teamsit --webhook "$TEAMS_WEBHOOK_URL" --text "Deploy finished"
```

## Title and Color

```bash
teamsit \
  --webhook "$TEAMS_WEBHOOK_URL" \
  --title "Deploy" \
  --color 0078D4 \
  --text "Hello, Teams!"
```

## MessageCard

```bash
teamsit --webhook "$TEAMS_WEBHOOK_URL" --card \
  '{"summary": "Deploy finished", "themeColor": "0078D4", "text": "All jobs passed"}'
```

## Validation Post

```bash
teamsit --webhook "$TEAMS_WEBHOOK_URL" --validate
```

This posts `This is a validation message`.

## Profiles

`$HOME/.teamsit.yml`:

```yaml
profiles:
  testing:
    webhook_url: https://outlook.office.com/webhook/YOUR_WEBHOOK_URL
    title: Alerts
    color: "00FF00"
  notices:
    webhook_url: https://contoso.webhook.office.com/webhookb2/YOUR_WEBHOOK_URL
    title: Notice
```

```bash
teamsit --profile testing --text "Hello, Teams!"
teamsit -p notices --config "$HOME/work/teamsit.yml" --text "Disk full"
teamsit -p testing --title "Other" --text "Override the profile title"
```

## Library

```python
from lupaxa.teamsit import Teamsit, load_profile

profile = load_profile("notices")
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
client.send_message("Hello\\nfrom the library")
```
