# AGENTS.md – ESPHome Firmware

Use this guide for everything under `esphome/`. Read `../CLAUDE.md` first; it
explains the project snapshot, documentation map, and two-machine workflow this
directory relies on.

## Before You Touch Firmware
1. Re-read `docs/ARCHITECTURE.md` and `docs/presence-engine-spec.md` to confirm
   state-machine, calibration, and telemetry requirements.
2. Check `docs/development-scorecard.md` for Phase 3/3.1+ objectives that may
   affect defaults or telemetry.
3. Note that firmware flashing/logs **must** happen on `ubuntu-node`; Codespaces
   is for editing + unit tests only (details in `docs/DEVELOPMENT_WORKFLOW.md`).

## Scope & Guardrails
- `custom_components/bed_presence_engine/`: C++ engine (Phase 3 deployed –
  automated MAD calibration, distance windowing, change-reason telemetry). Keep
  member naming (`snake_case_`) and logging style consistent.
- `packages/*.yaml`: Declarative wiring for hardware, presence engine, services,
  diagnostics. Mirrors Home Assistant entity IDs; update dashboards/blueprints
  + docs when changing defaults or names.
- `test/test_presence_engine.cpp`: PlatformIO native tests. Any state machine,
  timer, or calibration change requires matching unit coverage.
- Defaults to preserve unless spec changes: μ=6.7%, σ=3.5%, `k_on=9.0`,
  `k_off=4.0`, on/off debounce 3000/5000 ms, absolute clear 30000 ms, distance
  window `[0cm, 600cm]`.

## Required Checks Before You Push
- [ ] `cd esphome && platformio test -e native`
- [ ] `yamllint esphome/`
- [ ] Updated docs/tests/HA assets for any new entities, services, or defaults
      (quickstart, troubleshooting, dashboards, blueprints, E2E tests).
- [ ] Verified two-machine workflow steps in `docs/DEVELOPMENT_WORKFLOW.md`
      still match reality if you changed deployment commands.

## Useful Commands & Shortcuts
```bash
# Compile/flash (ubuntu-node only)
esphome run bed-presence-detector.yaml

# Stream logs (ubuntu-node only)
esphome logs bed-presence-detector.yaml

# Native unit tests (Codespaces OK)
cd esphome && platformio test -e native
```

## Common Pitfalls
- Forgetting to expose new runtime knobs via template numbers → HA controls
  break. Update `packages/presence_engine.yaml` and dashboard helpers together.
- Editing defaults without syncing docs, HA dashboards, and E2E tests.
- Trying to compile/flash inside Codespaces (blocked). Instead follow the
  workflow in `docs/DEVELOPMENT_WORKFLOW.md`.

Need more context? Jump back to `../CLAUDE.md` or the architecture/spec docs.
