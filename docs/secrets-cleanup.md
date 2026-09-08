# Move committed secrets into secrets.yaml

Status: **Planned**
Created: 2026-09-08
Priority: High (security — repo pushes to remote via `shell_command.git_update`)

## Problem

Live secrets are committed directly in `configuration.yaml` (and one ESPHome file)
instead of using `!secret` references. The `shell_command.git_update` command runs
`git add . && commit && push origin main`, so anything in these files is published to the
remote the moment it runs.

## Affected values

In `configuration.yaml`:
- SwitchBot REST command (`rest_command.switchbotdavebottista`): `authorization` token,
  `sign`, and `nonce` headers.
- Alexa Virtual Buttons 1–5 (`rest_command.alexavirtualbutton01`–`05`): the long
  `amzn1.ask.account...` `accessCode` values (currently duplicated across all five).

In `esphome/hascreen.yaml`:
- `api.encryption.key`
- `ota.password`

Note: the rest of the config already uses `!secret` correctly (Spotcast, Sigen modbus,
wifi) — this is just cleaning up the stragglers.

## Plan

1. Add the values to `secrets.yaml` with clear key names, e.g.:
   - `switchbot_dave_authorization`, `switchbot_dave_sign`, `switchbot_dave_nonce`
   - `alexa_virtual_button_access_code` (single shared key — all five reuse it)
   - `hascreen_api_encryption_key`, `hascreen_ota_password`
2. Replace the literals in `configuration.yaml` / `esphome/hascreen.yaml` with `!secret`.
3. Confirm `secrets.yaml` is in `.gitignore`.
4. **Rotate** the exposed tokens/keys if the repo history is or ever was public —
   moving them to `!secret` does not remove them from prior git history.

## Notes

- SwitchBot token/sign/nonce are time-based (`t`/`sign`/`nonce`) — verify the current
  values are still valid, or regenerate per the SwitchBot API signing scheme.
