# AGENTS.md

This file provides guidance to AI coding agents working with this repository. For comprehensive project details, see `CLAUDE.md`.

## Project Quick Reference

**Type**: IoT Hardware Project (ESP32 + LD2410 mmWave Sensor)
**Purpose**: Bed presence detection for Home Assistant using statistical z-score analysis
**Language Mix**: C++ (ESP32 firmware), Python (ESPHome/testing), YAML (configuration)
**Current Phase**: Phase 1 (z-score detection) - Fully implemented and tested
**Build System**: ESPHome + PlatformIO

## Essential Commands

### Firmware Development (from `esphome/` directory)
```bash
# Compile firmware (validates syntax and builds binary)
esphome compile bed-presence-detector.yaml

# Run C++ unit tests (14 tests, runs in ~5 seconds)
platformio test -e native

# Flash to physical device (requires connected ESP32)
esphome run bed-presence-detector.yaml

# View logs from connected device
esphome logs bed-presence-detector.yaml
```

### Testing
```bash
# C++ unit tests (fastest, no hardware needed)
cd esphome && platformio test -e native

# Python E2E tests (requires live Home Assistant)
cd tests/e2e
pip install -r requirements.txt
export HA_URL="ws://homeassistant.local:8123/api/websocket"
export HA_TOKEN="your-long-lived-access-token"
pytest

# YAML validation
yamllint esphome/ homeassistant/
```

### CI/CD
All pushes/PRs automatically trigger:
- ESPHome firmware compilation
- PlatformIO C++ unit tests
- YAML linting

## Repository Structure

```
/
├── esphome/                    # ESP32 firmware (see esphome/AGENTS.md)
│   ├── custom_components/
│   │   └── bed_presence_engine/   # C++ presence detection logic
│   ├── packages/                  # Modular YAML configuration
│   ├── test/                      # C++ unit tests (PlatformIO)
│   └── bed-presence-detector.yaml # Main ESPHome entry point
├── homeassistant/              # HA config (see homeassistant/AGENTS.md)
│   ├── blueprints/
│   └── dashboards/
├── tests/e2e/                  # Python integration tests (see tests/e2e/AGENTS.md)
├── docs/                       # Documentation (see docs/AGENTS.md)
├── hardware/mounts/            # 3D printable STL files (placeholders)
├── .github/workflows/          # CI/CD workflows
└── .devcontainer/              # GitHub Codespaces configuration
```

## Code Style Guidelines

### C++ (ESP32 Firmware)
- **Style**: ESPHome conventions (snake_case for variables, CamelCase for classes)
- **Headers**: Use `#pragma once` instead of include guards
- **Naming**:
  - Private member variables: trailing underscore (e.g., `k_on_`, `is_occupied_`)
  - Public methods: snake_case (e.g., `update_k_on()`)
  - Classes: CamelCase (e.g., `BedPresenceEngine`)
- **Comments**: Use `//` for single-line, `/* */` for multi-line
- **Logging**: Use ESPHome macros: `ESP_LOGD()`, `ESP_LOGI()`, `ESP_LOGW()`, `ESP_LOGE()`

### Python (Tests)
- **Style**: PEP 8
- **Formatting**: Use `black` for auto-formatting
- **Async**: Use `pytest-asyncio` for async tests
- **Assertions**: Prefer pytest's native assert over unittest assertions

### YAML (Configuration)
- **Indentation**: 2 spaces (enforced by yamllint)
- **Quotes**: Use double quotes for strings containing special characters
- **Comments**: Document non-obvious configuration choices
- **Secrets**: NEVER commit `secrets.yaml` - use `secrets.yaml.example` template

## Commit Message Guidelines

Format: `<type>: <subject>`

**Types**:
- `feat`: New feature (e.g., "feat: implement Phase 2 state machine")
- `fix`: Bug fix (e.g., "fix: correct z-score calculation in edge case")
- `test`: Add/modify tests (e.g., "test: add unit tests for hysteresis")
- `docs`: Documentation only (e.g., "docs: update calibration guide")
- `refactor`: Code restructuring without behavior change
- `style`: Formatting, whitespace (no code change)
- `chore`: Maintenance, dependency updates
- `ci`: CI/CD workflow changes

**Subject guidelines**:
- Use imperative mood ("add", not "added" or "adds")
- No period at the end
- Keep under 72 characters
- Reference issue numbers if applicable (e.g., "fix: correct baseline calc (#42)")

**Examples**:
```
feat: add Phase 2 debounce timers to state machine
fix: prevent division by zero in z-score calculation
test: add C++ unit tests for distance windowing
docs: document manual baseline calibration procedure
refactor: extract z-score calculation to separate method
```

## Security & Safety Considerations

### Secrets Management
- **CRITICAL**: NEVER commit `esphome/secrets.yaml`
- Store WiFi passwords, API keys, OTA passwords in `secrets.yaml` only
- Use `!secret` YAML tags in ESPHome configuration
- Template file: `esphome/secrets.yaml.example`

### Hardware Safety
- **Sensor**: LD2410 operates at 24GHz (safe for humans, FCC/CE compliant)
- **Power**: ESP32 powered via USB (5V) - no high voltage
- **GPIO**: All pins operate at 3.3V logic levels
- **UART**: RX/TX pins use 3.3V - verify LD2410 compatibility before wiring

### OTA (Over-The-Air) Updates
- Always set an OTA password in `secrets.yaml`
- ESPHome API encryption key required for Home Assistant integration
- Firmware is signed - ESPHome handles validation automatically

## Development Workflow

### Feature Development
1. **Create feature branch**: `git checkout -b feature/your-feature-name`
2. **Develop incrementally**:
   - For firmware: Compile → Test (C++) → Flash → Verify
   - For config: Validate YAML → Test in HA → Document changes
3. **Run tests**: Ensure all C++ unit tests pass
4. **Commit frequently**: Use clear commit messages
5. **Push and create PR**: CI/CD will validate your changes

### Bug Fixes
1. **Reproduce**: Add a failing unit test that demonstrates the bug
2. **Fix**: Modify code to make the test pass
3. **Verify**: Run full test suite to prevent regressions
4. **Document**: Update comments/docs if behavior changed

### Testing Strategy (Test Pyramid)
```
                  ┌────────────────┐
                  │  E2E Tests     │  Slowest, most comprehensive
                  │  (Python/HA)   │  Test full system integration
                  └────────────────┘
                 ┌──────────────────┐
                 │ ESPHome Compile  │  Medium speed
                 │ (Syntax/Build)   │  Validates configuration
                 └──────────────────┘
              ┌──────────────────────┐
              │   C++ Unit Tests     │  Fastest
              │   (PlatformIO)       │  Test logic in isolation
              └──────────────────────┘
```

**Recommended flow**: Unit tests → Compile → E2E tests (only if needed)

## Phase-Specific Development Notes

### Phase 1: Z-Score Detection (CURRENT - IMPLEMENTED)
**Status**: ✅ Complete and tested

**Key files**:
- `esphome/custom_components/bed_presence_engine/bed_presence.cpp` (96 lines)
- `esphome/custom_components/bed_presence_engine/bed_presence.h` (66 lines)
- `esphome/test/test_presence_engine.cpp` (219 lines, 14 tests)

**Characteristics**:
- Immediate state transitions (no debouncing)
- Hysteresis via `k_on` > `k_off` thresholds
- Manual baseline calibration (hardcoded μ, σ in code)
- Runtime tunable thresholds via Home Assistant

**When modifying Phase 1**:
- Update unit tests FIRST to reflect desired behavior
- Ensure all 14 existing tests still pass
- Test with actual hardware if changing z-score calculation
- Update default threshold values in both `.h` and `.yaml` files

### Phase 2: State Machine + Debouncing (PLANNED)
**Status**: ⏳ Not yet implemented

**Implementation guide**:
- See `docs/presence-engine-spec.md` Phase 2 section
- Requires adding state machine enum: `IDLE`, `DEBOUNCING_ON`, `PRESENT`, `DEBOUNCING_OFF`
- Add debounce timer entities to `packages/presence_engine.yaml`
- Refactor `bed_presence.cpp` to implement state machine logic
- Add time mocking to unit tests for testing debounce behavior

### Phase 3: Automated Calibration (PLANNED)
**Status**: ⏳ Service stubs exist but no implementation

**Implementation guide**:
- See `docs/presence-engine-spec.md` Phase 3 section
- Services defined in `packages/services_calibration.yaml` (currently just log messages)
- Implement baseline data collection in C++
- Use MAD (Median Absolute Deviation) for robust statistics
- Add calibration wizard UI to Home Assistant dashboard

## Common Pitfalls & Troubleshooting

### "Platform 'bed_presence_engine' not found"
**Cause**: ESPHome can't find custom component
**Fix**: Ensure you're running ESPHome from the `esphome/` directory
**Verify**: `ls custom_components/bed_presence_engine/` should show 4 files

### "Entity not found" in Home Assistant
**Cause**: Entity names don't match Phase 1 implementation
**Fix**: Use these Phase 1 entity names:
- `binary_sensor.bed_occupied`
- `number.k_on_on_threshold_multiplier`
- `number.k_off_off_threshold_multiplier`
- `text_sensor.presence_state_reason`

### Sensor is "twitchy" (rapid state changes)
**Cause**: Expected Phase 1 behavior (no debouncing)
**Fix**: Either:
  1. Adjust `k_on`/`k_off` thresholds for wider hysteresis
  2. Implement Phase 2 state machine with debounce timers

### Sensor never detects presence
**Cause**: Baseline statistics (μ, σ) don't match actual sensor readings
**Fix**: Follow manual calibration in `docs/phase1-hardware-setup.md`:
  1. Collect 30-60s of sensor data with empty bed
  2. Calculate mean and standard deviation
  3. Update `mu_move_` and `sigma_move_` in `bed_presence.h:43-46`
  4. Recompile and flash

### PlatformIO tests fail on clean checkout
**Cause**: Dependencies not installed
**Fix**: `cd esphome && platformio test -e native` (PlatformIO auto-installs deps on first run)

### E2E tests fail with "Connection refused"
**Cause**: Missing/incorrect Home Assistant connection details
**Fix**: Export required environment variables:
```bash
export HA_URL="ws://your-ha-instance:8123/api/websocket"
export HA_TOKEN="your-long-lived-access-token"
```

## Documentation Standards

### When to update documentation
- **Always**: When adding new features or changing user-facing behavior
- **Usually**: When fixing non-trivial bugs (explain the root cause)
- **Sometimes**: When refactoring (if it affects development workflow)
- **Never**: For internal refactoring that doesn't change behavior

### Documentation files
- `README.md`: User-facing quickstart and overview
- `CLAUDE.md`: Comprehensive developer guide (source of truth)
- `docs/presence-engine-spec.md`: Engineering specification (3-phase roadmap)
- `docs/phase1-hardware-setup.md`: Hardware wiring and calibration
- `docs/quickstart.md`, `docs/faq.md`, `docs/troubleshooting.md`: User guides
- `AGENTS.md` (this file): AI agent guidance

### Documentation style
- Use present tense ("This function calculates", not "This function will calculate")
- Include code examples for non-obvious usage
- Use blockquotes for warnings: `> **Warning**: This will erase calibration data`
- Link to related files/sections liberally
- Keep line length under 120 characters for readability

## Large Language Model (LLM) Specific Tips

### Context Management
- **Start here**: Read `CLAUDE.md` first for comprehensive project understanding
- **Phase verification**: Always check current phase status before suggesting features
- **File hierarchy**: Read headers (`.h`) before implementations (`.cpp`)
- **Test-driven**: Read unit tests to understand expected behavior

### Effective Code Generation
- **Don't guess entity names**: Search `packages/` directory for actual entity IDs
- **Match existing style**: Read surrounding code before generating new code
- **Preserve line numbers**: When editing, maintain existing structure to minimize diffs
- **Test your changes**: Always suggest running `platformio test` after C++ changes

### When uncertain
- **Check Phase boundaries**: Don't suggest Phase 2 features if Phase 1 isn't complete
- **Verify hardware**: Firmware compiles but hasn't been tested with actual hardware
- **Read specs**: `docs/presence-engine-spec.md` is the engineering source of truth
- **Ask first**: If a change affects multiple subsystems, outline the plan before implementing

## Contributing to This Repository

### For external contributors
1. **Fork the repository** on GitHub
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Run tests** to verify your changes
4. **Commit your changes** using conventional commit messages
5. **Push to your fork** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request** with a clear description

### For AI agents specifically
- **Phase awareness**: Current implementation is Phase 1 only
- **Test coverage**: All new C++ code requires unit tests
- **Documentation**: Update relevant docs when changing behavior
- **Breaking changes**: Clearly mark changes that affect existing users
- **Hardware limitations**: This project hasn't been tested with physical hardware yet

## Quick Reference Links

- **Project overview**: `README.md`
- **Developer guide**: `CLAUDE.md` (comprehensive, 400+ lines)
- **Engineering spec**: `docs/presence-engine-spec.md` (3-phase roadmap)
- **Hardware setup**: `docs/phase1-hardware-setup.md`
- **Firmware development**: `esphome/AGENTS.md`
- **HA configuration**: `homeassistant/AGENTS.md`
- **Testing guide**: `tests/e2e/AGENTS.md`
- **Documentation guide**: `docs/AGENTS.md`

## Environment Information

**GitHub Codespaces**: This repository is pre-configured for Codespaces. All required tools are automatically installed via `.devcontainer/devcontainer.json`.

**Local development requirements**:
- Python 3.11+
- ESPHome CLI: `pip install esphome`
- PlatformIO: `pip install platformio`
- pytest, pytest-asyncio: `pip install pytest pytest-asyncio`
- yamllint, black: `pip install yamllint black`

**Hardware requirements** (for physical testing):
- M5Stack Basic v2.7 or compatible ESP32 board
- LD2410C mmWave radar sensor
- USB cable for programming/power
- Jumper wires for UART connection (RX/TX)

---

**Need help?** See `CLAUDE.md` for detailed troubleshooting, or refer to subdirectory-specific `AGENTS.md` files for focused guidance.
