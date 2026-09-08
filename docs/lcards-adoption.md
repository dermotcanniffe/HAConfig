# Adopting LCARdS (successor to CB-LCARS)

Status: **In progress** — installed side-by-side with cb-lcars
Created: 2026-09-08
Source: https://github.com/snootched/lcards

## What it is

LCARdS is the official evolution of CB-LCARS, by the same author (snootched).
Per the project's own docs, it **originates from and supersedes CB-LCARS** — all
new features and fixes go to LCARdS only; CB-LCARS is frozen at its current version.
It's designed to accompany and complement the **ha-lcars theme** (which we already
have), so the theme layer is not wasted.

Caveat (from the repo): LCARdS is flagged work-in-progress and heavily AI-developed
(human-directed). It's a hobby project for personal use. CB-LCARS is currently the
more battle-tested of the two.

## Strategy: side-by-side, no big-bang migration

- Both cards can run simultaneously. Existing cb-lcars panels (e.g. the Ready Room)
  keep working untouched.
- Build NEW panels on LCARdS. Migrate old ones opportunistically, not all at once.
- Official CB-LCARS migration guide is linked from the LCARdS repo.

## Install (HACS)

1. HACS → Integrations → search "LCARdS" → Download
2. Restart Home Assistant
3. **Settings → Devices & Services → Add Integration → LCARdS**  ← REQUIRED

### Install gotcha (cost us several rounds — do not skip step 3)

LCARdS is a full **integration** (`config_flow: true`, `single_config_entry: true`),
NOT a plain frontend plugin like cb-lcars or a theme like ha-lcars. Consequences:

- It does NOT serve its card JS from `www/community/`. The bundle lives at
  `custom_components/lcards/lcards.js` and is served by the integration's
  `frontend.py` — which only runs once the config entry is ADDED and set up.
- Downloading in HACS + restarting is only HALF the install. Until you complete
  step 3, EVERY `lcards-*` card errors with "Custom element not found:
  lcards-button" (etc.), even though the files are on disk.
- Unlike cb-lcars/ha-lcars, LCARdS DOES appear under Settings → Devices &
  Services once added, and registers a sidebar panel.
- Card type names have NO `-card` suffix: `custom:lcards-button`,
  `custom:lcards-msd`, `custom:lcards-data-grid` (cb-lcars used `-card`; LCARdS
  dropped it).

Symptom → fix: "Custom element not found: lcards-*" for ALL cards →
Add Integration (step 3) → hard-refresh browser (Ctrl+Shift+R).
(Status: installed and config entry added — cards now resolve.)

## Cards of interest for this setup

| Card | Why it matters here |
|------|--------------------|
| `lcards-data-grid` | Tabular LCARS readout with live entity cells + cascade animation. Battery panel candidate — see `docs/dashboard-snippets/battery-status-panel-lcards.yaml`. |
| `lcards-msd` | Master Systems Display on a drawable SVG canvas — the native answer to the MSD dashboard goal. |
| `lcards-layout-view` | Whole-view visual grid editor (HA Sections-style) — addresses the "lots of work per dashboard" pain. |
| `lcards-chart` | ApexCharts with DataSource pipeline — for the derived energy sensors later. |
| `lcards-slider` / `lcards-button` / `lcards-elbow` | Direct replacements for the cb-lcars equivalents in existing panels. |

## Key API notes learned (data-grid)

- `data_mode: data` with an explicit `rows:` list of `[label, entity, template]`.
- Cells auto-detect type: static text, `sensor.entity_id` (live), `"{{ jinja }}"`,
  or `"{datasource:name}"`.
- No filter/match mechanism — rows are enumerated. For auto-populated "all batteries"
  keep the auto-entities panel; data-grid is for curated readouts.
- Scrolling: use the common props `max_height` + `overflow_y: auto` (LCARdS common
  card properties, not card_mod).
- Cascade sweep via `animations: [{trigger: on_load, preset: cascade-color}]`;
  live-change highlight via the separate top-level `animation:` key.

## Open follow-ups

- Decide MSD dashboard rebuild on `lcards-msd` (biggest new capability).
- Once comfortable, port the Ready Room panel from cb-lcars → LCARdS equivalents.
- Consider the patched `lovelace-layout-card` fork the LCARdS docs recommend if
  using `custom:layout-card` grids (upstream card_margin bug).
