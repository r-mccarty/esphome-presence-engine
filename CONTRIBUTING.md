# Contributing to Bed Presence Sensor

Thank you for your interest in contributing to this project! This guide will help you set up your development environment and understand the workflow.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Secrets Management](#secrets-management)
- [Development Commands](#development-commands)
- [CI/CD Workflows](#cicd-workflows)
- [Contributing Guidelines](#contributing-guidelines)

---

## Development Environment Setup

### GitHub Codespaces (Recommended)

This repository is pre-configured for **GitHub Codespaces**, which provides a fully configured development environment in the cloud.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/r-mccarty/bed-presence-sensor)

**What's included:**
- Python 3.11
- ESPHome CLI
- PlatformIO (for C++ unit testing)
- pytest, pytest-asyncio
- yamllint, black
- Claude CLI

**Setup is automatic** - just click the button above and wait for the container to build. All tools will be installed and configured.

### Local Development Setup

If you prefer to develop locally, you'll need to install the required tools manually:

**Requirements:**
- Python 3.11 or later
- pip package manager
- Git

**Installation steps:**

```bash
# Clone the repository
git clone https://github.com/r-mccarty/bed-presence-sensor.git
cd bed-presence-sensor

# Install Python dependencies
pip install esphome platformio pytest pytest-asyncio yamllint black homeassistant-api

# Verify installations
esphome version
platformio --version
pytest --version
```

---

## Secrets Management

**⚠️ CRITICAL:** This project uses **TWO different secrets files** for different purposes. Understanding the distinction is critical.

### Quick Reference: Which Secrets File Do I Need?

| File | Location | Purpose | Contains | Used By | Source of Truth |
|------|----------|---------|----------|---------|-----------------|
| **`.env.local`** | Project root | Python scripts access HA API | `HA_URL`, `HA_WS_URL`, `HA_TOKEN` | `collect_baseline.py`, E2E tests, monitoring scripts | **Ubuntu-node** |
| **`secrets.yaml`** | `esphome/` | WiFi credentials embedded in firmware | `wifi_ssid`, `wifi_password`, `api_encryption_key`, `ota_password` | ESPHome compiler | **Ubuntu-node** |

**Key Points:**
- These files are **completely unrelated** and serve different purposes
- Both are gitignored (contain sensitive credentials)
- **Ubuntu-node is the source of truth** for both files
- When working in Codespace, copy FROM ubuntu-node TO Codespace (never reverse)

---

### File 1: `.env.local` - Home Assistant API Access

**Purpose:** Python scripts need to connect to the Home Assistant REST/WebSocket API to read sensor values or control entities.

**Location:** `/workspaces/bed-presence-sensor/.env.local` (project root, gitignored)

**Contains:**
```bash
# Home Assistant Connection Configuration
HA_URL=http://192.168.0.148:8123
HA_WS_URL=ws://192.168.0.148:8123/api/websocket
HA_TOKEN=your-long-lived-access-token-here
```

**Used by:**
- `scripts/collect_baseline.py` - Collects LD2410 sensor readings from HA
- `tests/e2e/test_calibration_flow.py` - Integration tests
- Any script that needs to read/write HA entities

**How to get a Long-Lived Access Token:**
1. Open Home Assistant web UI → Profile (bottom left)
2. Scroll to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Name: "Bed Presence Development"
5. Copy the token (shown only once!)

**On Ubuntu-node** (source of truth):
```bash
# Already exists at ~/bed-presence-sensor/.env.local
cat ~/bed-presence-sensor/.env.local
```

**On Codespace** (copy from ubuntu-node):
```bash
# Copy .env.local FROM ubuntu-node TO Codespace
ssh ubuntu-node "cat ~/bed-presence-sensor/.env.local" > /workspaces/bed-presence-sensor/.env.local

# Verify
cat /workspaces/bed-presence-sensor/.env.local
```

**Never commit** `.env.local` to git (contains sensitive HA_TOKEN).

---

### File 2: `esphome/secrets.yaml` - WiFi Credentials for Firmware

**Purpose:** ESP32 device needs WiFi credentials to connect to your local network. These are embedded into the firmware binary during compilation.

**Location:** `/workspaces/bed-presence-sensor/esphome/secrets.yaml` (gitignored)

**Contains:**
```yaml
wifi_ssid: "TP-Link_BECC"
wifi_password: "your_wifi_password"
api_encryption_key: "base64-encoded-key-here"
ota_password: "your_ota_password"
```

**Used by:**
- ESPHome compiler (`esphome compile bed-presence-detector.yaml`)
- Credentials are burned into firmware during compilation
- ESP32 device uses these to connect to WiFi and Home Assistant

**On Ubuntu-node** (source of truth):
```bash
# Already exists at ~/bed-presence-sensor/esphome/secrets.yaml
cat ~/bed-presence-sensor/esphome/secrets.yaml
```

**On Codespace** (copy from ubuntu-node):
```bash
# Copy secrets.yaml FROM ubuntu-node TO Codespace
ssh ubuntu-node "cat ~/bed-presence-sensor/esphome/secrets.yaml" > /workspaces/bed-presence-sensor/esphome/secrets.yaml

# Verify
cat /workspaces/bed-presence-sensor/esphome/secrets.yaml
```

**Never commit** `secrets.yaml` to git (contains WiFi password).

---

### Why Two Files?

**Context 1: Python Scripts Running on a Computer**
- Scripts run on ubuntu-node or Codespace (regular computers with network access)
- Need to connect TO Home Assistant API over HTTP/WebSocket
- Use `.env.local` with `HA_URL` and `HA_TOKEN`

**Context 2: ESP32 Firmware Running on Embedded Device**
- Firmware runs on M5Stack ESP32 (embedded microcontroller)
- Needs WiFi credentials to join network and reach Home Assistant
- Uses `secrets.yaml` credentials embedded during compilation

**These are completely separate contexts with different tools and different needs.**

---

### Troubleshooting Secrets

**"collect_baseline.py fails with connection error"**
- Check that `.env.local` exists and has correct `HA_URL` and `HA_TOKEN`
- From Codespace: Use SSH tunnel (see DEVELOPMENT_WORKFLOW.md) OR run on ubuntu-node
- Verify token is valid in HA → Profile → Long-Lived Access Tokens

**"ESPHome compile fails - secrets.yaml not found"**
- Copy `secrets.yaml` from ubuntu-node: `ssh ubuntu-node "cat ~/bed-presence-sensor/esphome/secrets.yaml" > esphome/secrets.yaml`
- Or create from template: `cp esphome/secrets.yaml.example esphome/secrets.yaml` and fill in values

**"Which file do I edit?"**
- Changing WiFi network → Edit `esphome/secrets.yaml` (then recompile firmware)
- Changing HA access for scripts → Edit `.env.local` (no recompile needed)

---

## Development Commands

### ESPHome Firmware (run from `esphome/` directory)

**Compile firmware:**
```bash
cd esphome
esphome compile bed-presence-detector.yaml
```

**Run C++ unit tests (fully implemented):**
```bash
cd esphome
platformio test -e native
```

14 tests covering z-score calculation, state transitions, hysteresis, edge cases.

**Flash to device:**
```bash
cd esphome
esphome run bed-presence-detector.yaml
```

**⚠️ Note:** Flashing requires physical USB access. If using Codespaces, this must be done on ubuntu-node (see DEVELOPMENT_WORKFLOW.md).

---

### End-to-End Tests

```bash
cd tests/e2e
pip install -r requirements.txt  # Install dependencies including homeassistant-api
export HA_URL="ws://your-ha-instance:8123/api/websocket"
export HA_TOKEN="your-long-lived-access-token"
pytest  # Phase 3 tests will be skipped automatically
```

**Note:** E2E tests require a live Home Assistant instance with the device connected.

---

### Code Quality Tools

**YAML linting:**
```bash
yamllint esphome/ homeassistant/
```

**Python formatting:**
```bash
black tests/e2e/ scripts/
```

---

## CI/CD Workflows

### compile_firmware.yml (Functional)

**Triggers:** Push/PR to main affecting `esphome/**`

**Jobs:**
1. **compile**: Installs ESPHome, compiles `bed-presence-detector.yaml`
2. **test**: Installs PlatformIO, runs `platformio test -e native`

**Status:** ✅ Both jobs functional and passing

### lint_yaml.yml (Functional)

**Triggers:** Push/PR to main

**Jobs:** Runs `yamllint` on `esphome/` and `homeassistant/` directories

**Status:** ✅ Functional

---

## Contributing Guidelines

### Code Style

**C++:**
- Follow ESPHome coding conventions
- Use meaningful variable names
- Comment complex logic
- Update unit tests for any algorithm changes

**Python:**
- Use Black for formatting: `black tests/e2e/ scripts/`
- Follow PEP 8 guidelines
- Add docstrings to functions
- Include type hints where appropriate

**YAML:**
- Use 2 spaces for indentation
- Follow ESPHome YAML structure
- Validate with yamllint before committing

### Testing Requirements

**For C++ changes:**
- Update unit tests in `esphome/test/test_presence_engine.cpp`
- Ensure all tests pass: `platformio test -e native`
- Add new tests for new features

**For Python changes:**
- Update E2E tests in `tests/e2e/test_calibration_flow.py`
- Ensure tests pass: `pytest`
- Add new tests for new functionality

### Pull Request Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the code style guidelines
3. **Test your changes** (unit tests, E2E tests, manual testing)
4. **Update documentation** if adding new features or changing behavior
5. **Commit with clear messages** describing what and why
6. **Submit a PR** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/videos if relevant
   - Test results

### Areas for Contribution

**Phase 3 Implementation:**
- Automated baseline calibration via Home Assistant services
- MAD (Median Absolute Deviation) statistical analysis
- Distance windowing to ignore specific zones
- Calibration wizard UI

**Hardware Assets:**
- 3D printable mounts for various sensor positions
- Wiring diagrams and schematics
- Demo videos and GIFs

**Documentation:**
- Additional tuning guides
- Real-world deployment experiences
- Translation to other languages
- Video tutorials

**Testing:**
- Additional unit test coverage
- E2E test scenarios
- Performance testing
- Stress testing

---

## Getting Help

If you need help with development:

1. **Read the documentation:**
   - [Architecture](docs/ARCHITECTURE.md) - Technical details
   - [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md) - Workflow guide
   - [Troubleshooting](docs/troubleshooting.md) - Common issues

2. **Check GitHub Issues** for similar questions or problems

3. **Open a new issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs or screenshots

4. **Join the discussion** in existing issues or PRs

---

## License

By contributing to this project, you agree that your contributions will be licensed under the Apache 2.0 License.
