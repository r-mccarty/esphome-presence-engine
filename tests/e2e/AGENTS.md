# AGENTS.md – End-to-End Tests

Applies to everything under `tests/e2e/`. Review `../../CLAUDE.md` first, then
reference `docs/DEVELOPMENT_WORKFLOW.md` (two-machine flow) and
`docs/ARCHITECTURE.md` for entity/behavior expectations.

## Execution Rules
- Tests **must** run on `ubuntu-node`. Codespaces cannot reach the HA instance
  (192.168.0.148) or the ESPHome device.
- Use the shared virtualenv (`~/.venv-e2e`) and credentials in `~/.env.local`
  (`HA_URL`, `HA_TOKEN`). Ubuntu-node is the source of truth for these secrets.
- Ensure the production firmware (Phase 3) is flashed and online before running
  the suite.

## Running the Suite
```bash
ssh user@ubuntu-node
cd ~/bed-presence-sensor/tests/e2e
. ~/.venv-e2e/bin/activate
set -a && . ~/.env.local && set +a   # provides HA_URL/HA_TOKEN
pytest -v                            # full suite
pytest -v -k calibration             # targeted subset
```

## Coverage Expectations
- Phase 3 entities/services: binary sensor, state/change reason text sensors,
  runtime knob numbers (thresholds, debounce timers, distance window),
  MAD calibration services (`calibrate_start_baseline`, `calibrate_reset_all`).
- Future Phase 3.1+ work (calibration persistence, analytics) should add tests
  as features land—track gaps in `docs/development-scorecard.md`.
- Wizard helper flows remain partially manual; document any skipped coverage in
  `docs/troubleshooting.md`.

## Writing & Updating Tests
- Mirror firmware defaults (`k_on=9.0`, `k_off=4.0`, timers 3s/5s/30s, distance
  window `[0, 600]`). Update constants when defaults change.
- Use the shared `hass_ws.py` client; avoid third-party dependencies.
- Poll for state changes with bounded timeouts; avoid long `sleep()` calls.
- Reset knobs via `esphome.bed_presence_detector_calibrate_reset_all` between
  tests to keep runs independent.
- When adding entities/services in ESPHome, update:
  1. `tests/e2e/constants.py` (if present) or inline IDs.
  2. This AGENTS.md file.
  3. Relevant documentation (`docs/ARCHITECTURE.md`, `docs/quickstart.md`).

## Debugging Tips
- Connection failures? Verify HA is reachable (`wscat -c ws://192.168.0.148:8123/api/websocket`)
  and that the token in `~/.env.local` is valid.
- Missing entities? Confirm the ESPHome device is online and flashed with the
  latest firmware; compare IDs with `esphome/packages/presence_engine.yaml`.
- Flaky timing? Increase debounce timers temporarily or extend polling timeouts,
  but update assertions afterward so they reflect production behavior.

For additional context return to `../../CLAUDE.md` or the workflow/test sections
in the documentation set.
