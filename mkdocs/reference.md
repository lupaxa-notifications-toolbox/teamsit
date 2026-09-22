# Reference

## CLI arguments

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

The webhook URL must start with `https://outlook.office.com/webhook/`,
`https://outlook.office365.com/webhook/`, or use a
`.webhook.office.com/webhookb2/` address.
`--timeout` must be greater than `0`. `--color` is six hex digits, with or
without a leading `#`. One of `--text`, `--card`, or `--validate` is required.
Pass `--webhook`, or `--profile` with a `webhook_url` in the config file.
`--config` selects a file other than `$HOME/.teamsit.yml`. CLI flags override
the selected profile.

## Config file

The default path is `$HOME/.teamsit.yml`, from `default_config_path()`.
`--config` selects another file and requires `--profile`.

| Field         | Required                     | Meaning                                  |
| :------------ | :--------------------------- | :--------------------------------------- |
| `webhook_url` | unless `--webhook` is passed | Microsoft Teams incoming webhook URL     |
| `title`       | no                           | Card title                               |
| `color`       | no                           | Theme color; default `00FF00`            |
| `timeout`     | no                           | Request timeout in seconds; default `10` |

The file must contain a `profiles` mapping. Profile names are strings.
Unknown keys are rejected. CLI flags override the selected profile.

## Exit codes

| Code | When                                                         |
| :--- | :----------------------------------------------------------- |
| `0`  | Help, version, or Teams accepted the post                    |
| `1`  | The webhook was rejected, or the post failed                 |
| `2`  | Command-line usage, a bad config, or argument parsing failed |

## Library

| Name                  | Meaning                                                        |
| :-------------------- | :------------------------------------------------------------- |
| `Teamsit`             | Client bound to one incoming webhook                           |
| `send_message`        | Post text as a MessageCard, unescaping `\\n`                   |
| `send`                | Alias of `send_message`                                        |
| `send_card`           | Post one MessageCard from a JSON object string                 |
| `send_payload`        | POST a JSON object, filling card type and theme color          |
| `validate`            | HEAD the webhook, then post a validation message               |
| `valid_webhook`       | Return whether a URL answers `HEAD` without a redirect         |
| `convert_to_json`     | Parse a JSON string or raise `ValueError`                      |
| `is_teams_webhook`    | Return whether a URL is an accepted Teams webhook address      |
| `normalize_color`     | Return a 6-digit hex color without a leading `#`               |
| `DEFAULT_TIMEOUT`     | Default request timeout (`10.0`)                               |
| `DEFAULT_COLOR`       | Default theme color (`00FF00`)                                 |
| `WEBHOOK_PREFIX`      | Office 365 connector prefix                                    |
| `load_profile`        | Load one named profile from a YAML config file                 |
| `default_config_path` | Return `$HOME/.teamsit.yml`                                    |
| `ConfigError`         | Raised when the config file or profile cannot be used          |
| `Profile`             | Webhook settings stored for one profile                        |
| `get_version()`       | Return the package version string                              |

A Teams HTTP 200 response returns `True`. Redirects, an empty error body, Teams
error text, and invalid JSON raise `ValueError`. Network failures raise the
underlying `requests` exception. `validate` returns `False` when the follow-up
`HEAD` does not succeed.
