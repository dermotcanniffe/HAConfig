# Island Mode — "Critical Devices Only" Backup Power Optimisation

Status: **Planned** (blocked on Sigen hardware)
Owner: Dermot
Created: 2026-09-08

## Goal

When the grid drops and the house runs off solar + battery, automatically enter an
aggressive energy-saving mode that stretches battery runtime as far as possible by
managing the discretionary loads Home Assistant can control (lights, aircon, media,
chargers, plugs), while surfacing clear status (time remaining, current tier) to the
household.

## Two-layer architecture

This feature is split into two independent systems. Do not conflate them.

### Layer 1 — Hardware load shedding (NOT Home Assistant)

The physical separation of essential vs non-essential circuits is done by a
**Sigen ATS / Backup Gateway** wired into the consumer unit by an electrician:

- Essential loads (fridge/freezer, networking + HA host, boiler/heating controls, a
  handful of key lights and sockets) go on a **backup-protected sub-board**.
- On grid loss the gateway physically islands the house; the non-essential board goes
  dead on its own.
- HA must NOT be responsible for keeping essential loads (e.g. the fridge) alive — that
  cannot depend on HA being up.

**Blocker / prerequisite:** the Sigen system needs to be modified first — installation
and commissioning of the Backup Box / ATS and a decision, with the installer, on which
circuits sit on the protected board.

### Layer 2 — Software optimisation (Home Assistant — this task)

Once islanded, HA watches the grid status, flips into "island mode," and manages the
*discretionary* loads that remain energised to conserve battery.

## Signals already available (confirmed in config)

From `packages/modbus_sigenergy.yaml`:

- `sensor.sigen_on_off_grid_status` — "On grid" / "Off grid (auto)" / "Off grid (manual)"
  - backed by `sensor.sigen_on_off_grid_status_code` (0 / 1 / 2)
- `sensor.sigen_grid_sensor_status` — "Connected" / "Not connected"
  - backed by `sensor.sigen_grid_sensor_status_code` (0 / 1)
- `sensor.sigen_energy_storage_system_soc` — plant battery SOC %
- `sensor.sigen_general_alarm1` — includes code **1010 = Grid outage**
- `sensor.sigendev_rated_battery_capacity` — usable capacity (kWh) for runtime maths
- `sensor.sigen_battery_power` — <0 discharging, >0 charging (for load/runtime derivation)
- `sensor.sigen_pv_power`, `sensor.sigen_grid_sensor_active_power` — for house-load derivation

## Detection logic

Enter island mode when ANY of:
- `sensor.sigen_on_off_grid_status` != "On grid", OR
- `sensor.sigen_grid_sensor_status` == "Not connected", OR
- `sensor.sigen_general_alarm1` == "Grid outage" (code 1010), OR
- `input_boolean.island_mode_manual_test` is on (dry-run without pulling the mains)

Expose as a template `binary_sensor.on_backup_power`.

## Behaviour when island mode turns ON

1. **Announce** via existing TTS / assist satellites (reuse `script.speak_llm_response`
   pattern and `assist_satellite.*` / `tts.home_assistant_cloud`):
   "Grid power lost, running on battery, ~X hours remaining."
2. **Shed discretionary loads immediately** (final list TBD — see Open Questions):
   - aircon switch off
   - non-essential plugs: PlugBob, studio lights, Christmas lights, chargers
   - SwitchBots (Dave / Jerry) off
   - pause media players
3. **Aggressive lighting mode:**
   - drastically shorten "room empty -> lights off" timeouts (Office currently 5 min,
     Living Room presence off-delay short) — target ~60s while islanded
   - cap brightness (~40%) and force warm/low-power colour temp
4. **Tiered shedding by SOC** via `input_select.island_power_tier`:
   - Normal (on grid)
   - Conserve (< 40% SOC): shed loads above + dim lights
   - Critical (< 25% SOC): kill more lights, minimum brightness
   - Survival (< 15% SOC): warn that HA host itself may shut down soon

## Behaviour when island mode turns OFF (grid restored)

- Restore normal light-off timeouts / brightness caps.
- Un-inhibit everything.
- Do NOT auto-restore shed loads — let the household turn things back on deliberately.

## Proposed implementation: self-contained package

Create `packages/island_mode.yaml` (isolated from `automations.yaml`) containing:

- `input_boolean.island_mode_manual_test` — dry-run toggle
- `binary_sensor.on_backup_power` — template sensor per detection logic above
- `input_select.island_power_tier` — Normal / Conserve / Critical / Survival
- `sensor.battery_runtime_estimate` — derived: usable kWh (SOC x capacity) / current house
  load; used in announcements ("~3.5 hours left")
- Automations:
  - on-enter: shed loads + announce
  - SOC-tier escalation (drives `input_select.island_power_tier`)
  - fast empty-room light killer that ONLY runs while `binary_sensor.on_backup_power` is on
    (runs in parallel; leaves existing per-room automations untouched)
  - on-exit: restore timeouts / caps

Design rationale: a parallel island-mode automation set avoids editing the many existing
per-room presence automations. The alternative (a shared `input_number.light_off_delay`
helper referenced by every automation) is cleaner long-term but requires touching each
automation.

## Open questions to resolve before implementation

1. **Essential vs non-essential entity lists** — confirm which entities are discretionary
   (safe for HA to switch off on backup). Proposed to shed: aircon, PlugBob, studio lights,
   Christmas lights, SwitchBots (Dave/Jerry), chargers; pause media players. Anything to keep?
2. **Backup Gateway status** — is the Sigen ATS/Backup module installed yet? Determines
   whether "Off grid (auto)" will actually fire, or whether to lean on grid-sensor + alarm
   signals.
3. **Battery capacity source** — read `sensor.sigendev_rated_battery_capacity` dynamically,
   or hardcode usable kWh?
4. **Lighting aggressiveness** — hard-off empty rooms after ~60s and cap brightness ~40%,
   or keep gentler?

## Related follow-ups (from earlier review, not part of this task)

- Move committed secrets (SwitchBot token/sign/nonce, Alexa Virtual Button access codes,
  ESPHome api/ota keys) into `secrets.yaml`; rotate if repo history is public.
- Fix battery-threshold string comparison bug in `Batteries to Replace` /
  `Total Battery Devices` template sensors (string vs numeric `lt`).
- Add derived house-load + self-consumption sensors (foundation for cost/runtime maths).
