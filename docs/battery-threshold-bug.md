# Fix battery low-threshold comparison bug

Status: **Fixed** (2026-09-08) — pending live verification in Developer Tools > Template
Created: 2026-09-08
Priority: Medium (correctness — under-reports low batteries)

## Resolution

Rewrote both `sensor.batteries_to_replace` `state` and its `shopping_list` attribute
in `configuration.yaml` to iterate battery sensors in a loop and compare
`s.state | float(100) < low_threshold` (numeric), flagging `unavailable`/`unknown`
separately. Removed the invalid `select('test', 'any', ...)` construct and the
string comparison `('state', 'lt', low_threshold | string)`. Verify on the live
instance with the template snippet, then Check Configuration + reload.

## Problem

In `configuration.yaml`, the template sensors `Batteries to Replace` and
`Total Battery Devices` compare a battery `state` against `low_threshold | string`
using an `lt` (less-than) test. Because both sides are strings, the comparison is
lexicographic, not numeric: e.g. "9" sorts as greater than "20", so a battery at 9%
is NOT flagged as low. The low-battery count is therefore under-reported.

## Location

`configuration.yaml`, template section:
- `sensor.batteries_to_replace` (state + `shopping_list` attribute)
- possibly related logic in `sensor.total_battery_devices`

Look for patterns like:
```
('state', 'lt', low_threshold | string)
```

## Fix

Compare numerically instead of as strings. Cast the entity state with `| float` (or
`| int`) and compare to the numeric threshold, while still handling
`unavailable` / `unknown` states separately so they don't crash the cast.

Sketch:
```jinja
{% set low_threshold = 20 %}
{% set low = states.sensor
  | selectattr('attributes.device_class', 'eq', 'battery')
  | selectattr('state', 'in', ['unavailable', 'unknown'])
  | map(attribute='entity_id') | list %}
{% set drained = states.sensor
  | selectattr('attributes.device_class', 'eq', 'battery')
  | rejectattr('state', 'in', ['unavailable', 'unknown'])
  | selectattr('state', 'lt', low_threshold)   {# numeric compare after reject #}
  | map(attribute='entity_id') | list %}
```
(Exact form to be validated in the template editor — the key change is numeric
comparison, not `| string`.)

## Verify

Use Developer Tools > Template to confirm a known low/known-good battery is classified
correctly before/after.
