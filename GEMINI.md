# Gemini Code Assistant Context

This document provides a comprehensive overview of the Bed Presence Sensor project for the Gemini Code Assistant. It covers the project's purpose, architecture, key technologies, and development conventions.

## Project Overview

The Bed Presence Sensor is a high-reliability, tunable, and transparent bed-presence detection solution for Home Assistant. It uses an ESP32 microcontroller and an LD2410 mmWave radar sensor to detect presence.

The core of the project is a C++ statistical presence detection engine running on the ESP32. This engine uses z-score normalization to convert raw mmWave radar readings into statistical significance, combined with a 4-state machine for temporal filtering. This approach makes the detection resilient to environmental changes and false positives.

The project is deeply integrated with Home Assistant, allowing for real-time monitoring, tuning of parameters, and visualization of sensor data.

### Key Technologies

*   **Hardware:** ESP32 (M5Stack Basic), LD2410 mmWave radar sensor
*   **Firmware:** ESPHome, C++ for the custom presence engine
*   **Home Assistant:** YAML for configuration and dashboards
*   **Testing:** PlatformIO for C++ unit tests, Python with `pytest` for end-to-end tests
*   **CI/CD:** GitHub Actions for compiling firmware and linting YAML files

### Architecture

The project follows a 3-phase development roadmap:

*   **Phase 1 (Complete):** Z-score based detection with hysteresis.
*   **Phase 2 (Deployed):** State machine with debouncing for temporal filtering.
*   **Phase 3 (Deployed):** Automated calibration + distance windowing using MAD statistics.

The C++ presence engine implements a 4-state machine: `IDLE`, `DEBOUNCING_ON`, `PRESENT`, and `DEBOUNCING_OFF`. State transitions are determined by z-score values and debounce timers.

The ESPHome configuration is modular, with separate YAML files for hardware, the presence engine, services, and diagnostics.

## Building and Running

The recommended development environment is GitHub Codespaces, which comes pre-configured with all the necessary tools.

### Key Commands

All commands should be run from the project's root directory.

**Compile Firmware:**
```bash
cd esphome
esphome compile bed-presence-detector.yaml
```

**Run C++ Unit Tests:**
```bash
cd esphome
platformio test -e native
```

**Flash Firmware (ubuntu-node only):**
```bash
ssh ubuntu-node
~/sync-and-flash.sh   # wraps git pull + esphome run
```
*(Codespaces cannot access the USB-connected ESP32.)*

**Run End-to-End Tests (ubuntu-node):**
```bash
ssh ubuntu-node
cd ~/bed-presence-sensor
. .venv-e2e/bin/activate
set -a && . .env.local && set +a   # provides HA_URL/HA_TOKEN
cd tests/e2e
pytest -v
```
- Uses the repo’s `tests/e2e/hass_ws.py` WebSocket helper
- Requires network access to `http://192.168.0.148:8123`

**Linting:**
```bash
yamllint esphome/ homeassistant/
black tests/e2e/ scripts/
```

## Development Conventions

*   **Secrets Management:** The project uses two separate secrets files:
    *   `.env.local` at the project root (and copied to ubuntu-node) for Home Assistant API access.
    *   `esphome/secrets.yaml` on ubuntu-node for WiFi credentials embedded in firmware.
*   **C++ Style:** Follow ESPHome coding conventions. Update unit tests for any algorithm changes.
*   **Python Style:** Use Black for formatting. Follow PEP 8 guidelines.
*   **YAML Style:** Use 2 spaces for indentation. Validate with `yamllint`.
*   **Testing:** All C++ changes must be accompanied by unit tests. All Python changes should have corresponding end-to-end tests.
*   **Pull Requests:** PRs should include a clear description of changes, link to related issues, and test results.

## Home Assistant Configuration Notes

* The live Home Assistant instance runs on ubuntu-node (Docker container) with config stored at `/opt/homeassistant/config`.
* Include `homeassistant/configuration_helpers.yaml` via:
  ```yaml
  homeassistant:
    packages:
      bed_presence_helpers: !include configuration_helpers.yaml
  ```
* After copying helper files or dashboards, restart the container with `sudo docker restart homeassistant`.
