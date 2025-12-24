# AI Agent Context Guide

This is the canonical orientation document for every AI agent working in this
repository. `CLAUDE.md`, `GEMINI.md`, and the root `AGENTS.md` all point to this
same content—consult any one of them before you start a task.

## 1. Current Snapshot
- **Product**: ESP32 + LD2410 bed-presence detector with ESPHome firmware and Home
  Assistant integrations.
- **Phase**: Phase 3 (automated calibration, distance windowing, change-reason
  telemetry) is fully deployed. Phase 3.1+ efforts focus on calibration
  persistence, analytics, and operational monitoring. For historical details and
  remaining wishlist items, see `docs/development-scorecard.md`.
- **Baseline defaults**: μ=6.7%, σ=3.5%, `k_on=9.0`, `k_off=4.0`,
  `on_debounce=3s`, `off_debounce=5s`, `abs_clear=30s`, distance window
  `[0cm, 600cm]`. Confirm any future changes in `docs/ARCHITECTURE.md` and the
  ESPHome packages.

## 2. Orientation Checklist
1. **Understand the feature area**  
   Start with the document that matches your task:
   - `docs/ARCHITECTURE.md` – Presence-engine design, state machine, tests.
   - `docs/presence-engine-spec.md` – Formal multi-phase requirements.
   - `docs/development-scorecard.md` – Timeline + validation evidence.
   - `docs/DEVELOPMENT_WORKFLOW.md` – Two-machine (Codespaces ↔ ubuntu-node)
     workflow, flashing, network tunneling.
   - `docs/HARDWARE_SETUP.md` – Wiring, calibration environment.
   - `docs/troubleshooting.md` – Operational runbooks and diagnostics.
   - `docs/quickstart.md`, `docs/faq.md`, `docs/calibration.md` – Operator-facing
     onboarding and workflows.

2. **Check directory-specific guidance**  
   Every major subdirectory (`docs/`, `esphome/`, `homeassistant/`, `tests/e2e/`,
   etc.) has its own `AGENTS.md`. Follow those instructions before editing files
   inside the directory.

3. **Sync with current phase goals**  
   If your work touches lifecycle items (calibration history, analytics,
   monitoring), reference the Phase 3.1+ objectives in the scorecard and the
   corresponding sections in `docs/presence-engine-spec.md`.

## 3. Coder Workspace Environment

When running in a Coder workspace on the N100 node (`coder.hardwareos.com`):

### Pre-configured Access
| Service | Status | Notes |
|---------|--------|-------|
| **GitHub CLI** | Authenticated | `gh` commands work, account: `r-mccarty` |
| **Infisical Secrets** | Pre-loaded | All secrets exported to `~/.env.secrets` at startup |

### Luckfox Pico Max Access
The Luckfox Pico Max (RV1106G3) is connected via USB to the N100 host.

| Method | Status | Command |
|--------|--------|---------|
| **ADB** | ✅ Working | `sudo adb shell` |
| **SSH** | ❌ Not available | SSH service not running on Buildroot image |
| **Ping** | ✅ After IP setup | `ping 172.32.0.93` |

**First-time setup** (if ping fails):
```bash
sudo ip addr add 172.32.0.1/24 dev enx5aef472011ac
```

**ADB access** (restart server if permission denied):
```bash
adb kill-server && sudo adb start-server
sudo adb shell
```

For detailed setup, see `docs/luckfox-pico-max-setup.md` and `docs/n100-coder-access.md`.

### Related: HardwareOS RS-1 HIL Testing

This workspace also hosts the **hardwareOS** repo for RS-1 vision pipeline HIL testing.
The Luckfox Pico Max serves as the RS-1 dev board target.

| Resource | Location |
|----------|----------|
| hardwareOS repo | `/home/coder/workspace/hardwareOS` |
| Camera HIL plan | `hardwareOS/docs/rs1/CAMERA_HIL_INTEGRATION.md` |
| Camera sensors | `hardwareOS/docs/rs1/CAMERA_SENSORS.md` |
| RoomPlan HIL | `hardwareOS/docs/rs1/ROOMPLAN_INTEGRATION_TESTING.md` |

See the hardwareOS `CLAUDE.md` for RS-1 development workflows.

## 4. Workflow Highlights
- **Two-machine rule**: Code editing and docs happen in Codespaces; firmware
  builds, flashing, and anything that needs Home Assistant access must run on
  `ubuntu-node`. Details live in `docs/DEVELOPMENT_WORKFLOW.md`.
- **Secrets**: `.env.local` (HA API) and `esphome/secrets.yaml` (WiFi/API/OTA)
  are sourced from ubuntu-node. Never push secrets; instructions reside in
  `CONTRIBUTING.md`.
- **Testing**:  
  - `cd esphome && platformio test -e native` for C++ unit tests.  
  - `yamllint esphome/ homeassistant/` for YAML validation.  
  - `tests/e2e/` suites (run on ubuntu-node) cover HA interactions; wizard UI
    flow still requires manual verification per `docs/troubleshooting.md`.
- **Coding standards**: ESPHome C++ style (trailing `_` for members), YAML
  2-space indent, Python formatted with Black/PEP 8. Add or update tests for any
  behavior changes and document them in the relevant guide.

## 5. When Updating Documentation
- Prefer targeted docs instead of bloating this file. Historical context → scorecard,
  workflow steps → `docs/DEVELOPMENT_WORKFLOW.md`, hardware specifics →
  `docs/HARDWARE_SETUP.md`, troubleshooting tips → `docs/troubleshooting.md`.
- Keep Markdown lines ≤120 chars, use fenced code blocks with language hints, and
  follow the warning pattern `> **Warning**: ...` as described in `docs/AGENTS.md`.

## 6. Getting Help
If you encounter conflicting instructions or unexpected repository state:
1. Re-read the directory `AGENTS.md`.
2. Check open issues/notes in `docs/development-scorecard.md`.
3. Ask the user for clarification before making assumptions that could desync
   firmware, documentation, and Home Assistant configuration.
