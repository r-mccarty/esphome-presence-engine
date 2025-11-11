# Presence Detection Engine

[![Compile Firmware](https://github.com/r-mccarty/presence-dectection-engine/actions/workflows/compile_firmware.yml/badge.svg?branch=main&event=push)](https://github.com/r-mccarty/presence-dectection-engine/actions/workflows/compile_firmware.yml)
[![Lint YAML](https://github.com/r-mccarty/presence-dectection-engine/actions/workflows/lint_yaml.yml/badge.svg?branch=main&event=push)](https://github.com/r-mccarty/presence-dectection-engine/actions/workflows/lint_yaml.yml)

An open ESPHome/ESP32 presence engine that combines mmWave radar telemetry, on-device z-score analysis, and a debounced 4-state machine to deliver reliable occupancy signals for Home Assistant. The current reference configuration targets bed presence using an LD2410 sensor, but the architecture, tuning controls, and Home Assistant tooling are designed to generalize to other localized presence use cases.

## Project Snapshot

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | Z-score detector with hysteresis & runtime thresholds | ✅ Complete |
| Phase 2 | Debounced 4-state machine + absolute clear guard | ✅ Deployed |
| Phase 3 | MAD-based auto calibration, distance windowing, change-reason telemetry | ✅ Deployed |
| Phase 3.1+ | Calibration persistence, analytics, monitoring | 🔄 Planning |

See the [Development Scorecard](docs/development-scorecard.md) for release dates, validation evidence, and upcoming work.

## Why This Engine?

- **Fully on-device analytics** – μ/σ maintenance, z-scores, and state transitions happen on the ESP32, so automations react instantly even if Home Assistant is offline.
- **Transparent decision-making** – `Presence State Reason` and `Presence Change Reason` text sensors expose z-scores, debounce timers, absolute-clear timers, and calibration events.
- **Runtime tuning everywhere** – Thresholds, debounce durations, absolute-clear delay, and the distance window are all `number` entities you can adjust live in Home Assistant.
- **Guided calibration** – MAD-based baseline collection is wrapped in ESPHome services plus a Home Assistant wizard with helper entities, buttons, and status telemetry.
- **Two-machine workflow ready** – Codespaces stays focused on editing/tests, while ubuntu-node handles flashing, HA API access, and hardware interactions.
- **Tested & documented** – 16 PlatformIO unit tests cover the engine, with Python E2E tests validating the HA integration; documentation spans quickstart, workflow, hardware, and troubleshooting guides.

## Documentation Map

| Doc | Purpose |
|-----|---------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Deep dive on the C++ engine, z-score math, and testing strategy |
| [docs/presence-engine-spec.md](docs/presence-engine-spec.md) | Phase requirements and acceptance criteria |
| [docs/development-scorecard.md](docs/development-scorecard.md) | Historical log + Phase 3.1+ objectives |
| [docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md) | Codespaces ↔ ubuntu-node workflow (flashing, logs, tunneling) |
| [docs/HARDWARE_SETUP.md](docs/HARDWARE_SETUP.md) | Wiring, reference mounting, calibration environment |
| [docs/quickstart.md](docs/quickstart.md) | Operator onboarding for firmware + Home Assistant |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Runbooks for common sensor/HA issues |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Environment setup, secrets, CI expectations |

## Getting Started

### 1. Assemble Hardware

Follow the [Hardware Setup](docs/HARDWARE_SETUP.md) guide for wiring the LD2410 to an M5Stack (ESP32) or another ESP32 board. The defaults assume the still-energy channel is pointed at a bed, but you can re-mount and retune for other zones.

**Required components**
- ESP32 dev kit (M5Stack Basic reference build)
- LD2410 mmWave radar sensor
- USB cable for flashing/logs
- 4x jumper wires for UART (TX/RX/5V/GND)

### 2. Prepare the Development Environment

Use GitHub Codespaces (preconfigured) or a local environment described in [CONTRIBUTING.md](CONTRIBUTING.md).

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/r-mccarty/presence-dectection-engine)

Secrets live on `ubuntu-node`:
- `esphome/secrets.yaml` – WiFi/AP/OTA credentials for firmware
- `.env.local` – Home Assistant API access for Python tooling/tests

### 3. Build, Test, and Flash (Two-Machine Workflow)

1. **Codespaces / local editing**
   ```bash
   cd esphome
   platformio test -e native          # C++ unit tests
   yamllint esphome/ homeassistant/   # YAML checks
   ```
2. **Commit and push your changes.**
3. **ubuntu-node (hardware + HA access)**
   ```bash
   ssh user@ubuntu-node
   cd ~/presence-dectection-engine
   git pull
   esphome run esphome/bed-presence-detector.yaml   # compile + flash
   esphome logs esphome/bed-presence-detector.yaml  # verify runtime
   ```
4. **Home Assistant** – import/update dashboard, helpers, and blueprints from the `homeassistant/` directory, then monitor the change-reason sensors while you fine-tune thresholds.

Detailed steps live in [docs/DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md).

### 4. Integrate with Home Assistant

1. Allow ESPHome auto-discovery to add the device, enter the API key from `secrets.yaml`, and confirm entities appear.
2. Deploy the Lovelace dashboard (`homeassistant/dashboards/bed_presence_dashboard.yaml`) for live charts, tuning controls, and the Calibration Wizard.
3. Use the calibration helpers (`homeassistant/configuration_helpers.yaml`) to run MAD baseline collection, reset defaults, or widen the distance window when experimenting.
4. Automate with the blueprint under `homeassistant/blueprints/automation/`.

Consult the [Quickstart](docs/quickstart.md) for the full workflow and screenshots.

## Repository Layout

```
.
├── docs/                  # Specs, architecture, workflow, quickstart, troubleshooting
├── esphome/               # Firmware: custom component, packages, PlatformIO tests
├── homeassistant/         # Dashboards, blueprints, helper definitions
├── tests/e2e/             # Python HA integration tests (ubuntu-node only)
├── scripts/               # Utilities (e.g., legacy baseline collection)
├── hardware/              # CAD placeholders for mounts/enclosures
├── CLAUDE.md              # Canonical AI agent context (mirrored as AGENTS.md/GEMINI.md)
└── README.md              # You are here
```

## Contributing

We welcome improvements in four main areas:
1. **Core engine** – new telemetry, better analytics, configurable heuristics for non-bed scenarios.
2. **Calibration persistence + analytics** – Phase 3.1+ work to store baseline history, expose restlessness metrics, or add alerts.
3. **Home Assistant UX** – dashboard/blueprint refinements, onboarding flows, and helper automation coverage.
4. **Docs & assets** – diagrams, CAD mounts, troubleshooting guides, and translations.

Before opening a PR:
- Run unit tests/YAML lint, describe the two-machine workflow you followed, and list the tests you executed.
- Update documentation and Home Assistant assets for any behavioral changes.
- Follow conventional commits (`type: subject`) and keep subjects ≤72 characters.

See [CONTRIBUTING.md](CONTRIBUTING.md) for secrets management, environment setup, and CI details.

## License

Apache 2.0 – see [LICENSE](LICENSE) for details.

## Helpful Links

- [Architecture](docs/ARCHITECTURE.md)
- [Development Scorecard](docs/development-scorecard.md)
- [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)
- [Hardware Setup](docs/HARDWARE_SETUP.md)
- [Quickstart](docs/quickstart.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Issues](https://github.com/r-mccarty/presence-dectection-engine/issues)
