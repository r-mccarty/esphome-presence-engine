# AGENTS.md – Home Assistant Assets

This guide covers everything under `homeassistant/` (dashboards, blueprints,
helpers). Start with `../CLAUDE.md` for repo-wide context, then pull any
technical specifics from `docs/ARCHITECTURE.md`, `docs/quickstart.md`,
`docs/troubleshooting.md`, and `docs/presence-engine-spec.md`.

## Scope
```
homeassistant/
├─ dashboards/bed_presence_dashboard.yaml      # Lovelace dashboard + calibration wizard
├─ blueprints/automation/bed_presence_*.yaml   # Automation templates
└─ configuration_helpers.yaml                  # Helpers/scripts backing the wizard
```

## Editing Checklist
- [ ] Entity IDs and defaults exactly match `esphome/packages/presence_engine.yaml`
      (Phase 3 runtime knobs + distance window, Phase 3.1+ analytics placeholders).
- [ ] Dashboard layout keeps the workflow order: Status → Knobs → Debounce →
      Distance window → Diagnostics → Calibration wizard.
- [ ] Blueprint inputs/actions documented; breaking changes documented in
      `docs/quickstart.md` + release notes.
- [ ] Calibration helpers call the correct ESPHome services
      (`calibrate_start_baseline`, `calibrate_stop`, `calibrate_reset_all`).
- [ ] Any UI/behavior changes reflected in `docs/quickstart.md`,
      `docs/troubleshooting.md`, and E2E tests.

## Style & Validation
- YAML with 2-space indentation, descriptive labels (render directly in the HA UI).
- Prefer `!include`-friendly patterns so ubuntu-node deployments stay simple.
- Validate before committing:
  ```bash
  yamllint homeassistant/
  ```
- For live testing (ubuntu-node):
  1. Copy dashboard YAML into HA Raw Config Editor.
  2. Import blueprint via HA UI.
  3. Reload helpers (`configuration_helpers.yaml`) through Home Assistant
     packages and restart the HA container if necessary.

## Common Pitfalls
- **Entity drift**: Renaming entities in ESPHome without updating dashboard,
  blueprint, helpers, docs, and tests leads to broken UI cards. Always change
  them in lockstep.
- **Wizard regressions**: Calibration wizard relies on helper entities defined
  here; update `tests/e2e` when you modify helper names or wizard flow.
- **Missing two-machine context**: When documenting HA steps, specify they run
  on `ubuntu-node` (per `docs/DEVELOPMENT_WORKFLOW.md`).

Need more detail? Jump back to `../CLAUDE.md` and the docs listed above.
