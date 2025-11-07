# Calibration Guide

Reliable calibration keeps the z-score based detector stable across different rooms and beds. This guide
describes how the current Phase 1 and Phase 2 workflow operates today and highlights the planned Phase 3
automation.

## Phase Overview

- **Phase 1 (baseline z-score) and Phase 2 (state machine + debouncing)** use a **semi-automated script** to
  capture a vacant-bed baseline and then require a manual firmware update + Home Assistant tuning.
- **Phase 3 (planned)** will replace the script/manual steps with an in-dashboard calibration wizard that
  guides the operator through vacant/occupied sampling and writes results back automatically.

> **Note:** The script-driven process intentionally focuses on the vacant baseline. Occupied validation is
> performed manually by watching the Home Assistant entities after flashing the updated firmware.

## Phase 1 & 2 Calibration Workflow (Current)

### 1. Prepare the environment

1. Place the LD2410 sensor in its deployment location and verify it reports `ld2410_still_energy` in Home
   Assistant.
2. Empty the bed completely (no people, pets, or objects) and close the bedroom door to reduce motion.
3. Run calibration from the Ubuntu node that has network access to Home Assistant and (if needed) USB access
   to the M5Stack.

### 2. Collect a vacant baseline with the script

```bash
ssh ubuntu-node
cd ~/bed-presence-sensor
export HA_TOKEN="<your-long-lived-token>"
python3 scripts/collect_baseline.py
```

The script samples 30 still-energy readings over 60 seconds, prints the mean (`μ`) and standard deviation
(`σ`), and generates a ready-to-paste code snippet. Results are also saved to `baseline_results.txt` for
auditing.

### 3. Apply baseline constants to the firmware

1. Copy the four `mu_*` / `sigma_*` lines from the script output.
2. Update the defaults in `esphome/custom_components/bed_presence_engine/bed_presence.h`.
3. Commit the change so the collected baseline is tracked alongside firmware updates.

The `mu_still_` / `sigma_still_` values drive the z-score calculation for both Phase 1 and Phase 2. The
`mu_stat_` / `sigma_stat_` placeholders remain aligned with the same numbers until Phase 3 introduces moving
energy fusion.

### 4. Recompile, flash, and confirm telemetry

```bash
cd esphome
esphome compile bed-presence-detector.yaml
esphome run bed-presence-detector.yaml  # Flash via USB from ubuntu-node
```

After flashing, confirm that Home Assistant shows fresh sensor updates for `sensor.bed_presence_detector_`
entities and that the binary sensor reports `OFF` while the bed stays empty.

### 5. Tune thresholds and timers from Home Assistant

1. Lie in bed and verify `binary_sensor.bed_presence_detector_bed_occupied` transitions to `ON` after the
   on-debounce interval completes (3 s by default in Phase 2).
2. Use the device controls exposed by the ESPHome integration to refine behavior:
   - `k_on (ON Threshold Multiplier)` slider widens or narrows the entry threshold.
   - `k_off (OFF Threshold Multiplier)` slider governs how quickly the system clears when energy drops.
   - Phase 2 only: adjust `On Debounce Timer (ms)`, `Off Debounce Timer (ms)`, and `Absolute Clear Delay (ms)`
     number inputs if you need slower or faster transitions.
3. Document any non-default values so they can be reapplied after firmware updates.

If the binary sensor chatters while occupied, increase `k_on` or lengthen the on-debounce timer. If it takes
too long to clear after leaving the bed, lower `k_off` or shorten the off-debounce/absolute clear delays.

## Maintenance Cadence

- Re-run the script whenever the bedroom layout, mattress, or sensor placement changes materially.
- Re-verify thresholds seasonally if bedding thickness or HVAC patterns alter the still-energy baseline.
- Store the generated `baseline_results.txt` snapshots in version control for traceability.

## Looking Ahead to Phase 3

Phase 3 will deliver an interactive calibration wizard inside Home Assistant. It will:

- Orchestrate vacant and occupied sampling without leaving the dashboard.
- Update firmware baseline constants and helper entities automatically.
- Provide recommended threshold/debounce values derived from Median Absolute Deviation (MAD) analysis.

Until that wizard ships, continue using the script-driven workflow described above for reliable Phase 1 and
Phase 2 operation.
