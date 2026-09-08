# Add derived house-load and self-consumption sensors

Status: **Planned**
Created: 2026-09-08
Priority: Medium (foundation for cost, runtime, and load-shifting features)

## Goal

Derive the "missing" energy sensors from the raw Sigen Modbus data already being read.
These are the foundation for later features: live cost/savings, battery runtime estimate
(needed by Island Mode), and solar-surplus load shifting.

## Available raw inputs (from packages/modbus_sigenergy.yaml)

- `sensor.sigen_pv_power` — PV generation (kW)
- `sensor.sigen_battery_power` — <0 discharging, >0 charging (kW)
- `sensor.sigen_grid_sensor_active_power` — >0 import, <0 export (kW)
- `sensor.sigen_energy_storage_system_soc` — battery SOC (%)
- `sensor.sigendev_rated_battery_capacity` — usable capacity (kWh)
- daily/accumulated import/export/charge/discharge energy sensors

## Sensors to add (template)

1. **House load (kW)** — total on-site consumption:
   `load = pv + grid_import - grid_export + battery_discharge - battery_charge`
   (careful with sign conventions on `sigen_grid_sensor_active_power` and
   `sigen_battery_power`; validate against a known load).
2. **Self-consumption rate (%)** — PV used on-site / total PV generated.
3. **Solar autonomy (%)** — `1 - (grid_import / total_consumption)`.
4. **Battery time-to-empty / time-to-full** — from SOC, capacity, and current battery
   power. (Island Mode's runtime estimate reuses this.)
5. **"Cheap energy now" boolean** — true when SOC high or PV exporting; used as a
   condition for auto-running high-draw appliances (rice cooker, dishwasher, EV charging).

## Optional: cost/savings

If a tariff is added (day/night or dynamic Irish plan), combine with grid import/export
to produce "€ saved today by solar+battery." Consider HA's built-in Energy dashboard
cost config plus a template for the savings figure.

## Notes

- Put these in a package (e.g. `packages/derived_energy.yaml`) rather than inline in
  `configuration.yaml`, to keep the template section manageable.
- Validate sign conventions empirically — Sigen's >0/<0 meanings are documented per
  register in the modbus package comments.
