# AGENTS.md - ESPHome Firmware

This file provides guidance for AI agents working specifically with the ESP32 firmware in this directory.

## Overview

This directory contains the complete ESPHome firmware for the bed presence detector. The core presence detection logic is implemented in C++ as a custom ESPHome component, with modular YAML configuration for different subsystems.

## Quick Commands (run from this directory)

```bash
# Compile firmware (validates YAML and builds binary)
esphome compile bed-presence-detector.yaml

# Run C++ unit tests (fast, no hardware required)
platformio test -e native

# Flash to connected ESP32 device
esphome run bed-presence-detector.yaml

# View live logs from connected device
esphome logs bed-presence-detector.yaml

# Validate YAML only (no compilation)
esphome config bed-presence-detector.yaml

# Clean build artifacts
esphome clean bed-presence-detector.yaml
```

## Directory Structure

```
esphome/
├── bed-presence-detector.yaml       # Main entry point (includes packages)
├── secrets.yaml.example             # Template for WiFi/API credentials
├── secrets.yaml                     # Actual secrets (gitignored)
├── platformio.ini                   # PlatformIO configuration for unit tests
├── custom_components/
│   └── bed_presence_engine/         # Core C++ presence detection logic
│       ├── __init__.py              # ESPHome component registration
│       ├── binary_sensor.py         # ESPHome YAML schema definition
│       ├── bed_presence.h           # C++ header (class definition)
│       └── bed_presence.cpp         # C++ implementation (core logic)
├── packages/                        # Modular YAML configuration
│   ├── hardware_m5stack_ld2410.yaml # UART, GPIO, LD2410 sensor config
│   ├── presence_engine.yaml         # k_on/k_off threshold entities
│   ├── services_calibration.yaml   # Placeholder calibration services
│   └── diagnostics.yaml             # Device health/uptime sensors
└── test/
    └── test_presence_engine.cpp     # PlatformIO unit tests (14 tests)
```

## Critical Files

### bed-presence-detector.yaml
**Purpose**: Main ESPHome configuration entry point
**What it does**: Includes package files and sets device-wide settings
**When to modify**:
- Changing device name or friendly names
- Adding device-wide features (web server, logger settings)
- Adding new package includes

**Key sections**:
```yaml
esphome:
  name: bed-presence-detector
  friendly_name: Bed Presence Detector

packages:
  hardware: !include packages/hardware_m5stack_ld2410.yaml
  presence_engine: !include packages/presence_engine.yaml
  calibration: !include packages/services_calibration.yaml
  diagnostics: !include packages/diagnostics.yaml
```

### custom_components/bed_presence_engine/bed_presence.cpp
**Purpose**: Core C++ implementation of Phase 1 z-score detection
**Lines**: 96 lines
**Key logic**: `process_energy_reading()` method (lines 47-77)

**Algorithm**:
1. Calculate z-score: `z = (energy - μ) / σ`
2. Check threshold with hysteresis:
   - Turn ON if `z > k_on`
   - Turn OFF if `z < k_off`
   - Stay in current state if `k_off < z < k_on` (hysteresis zone)
3. Publish state and reason to Home Assistant

**Critical variables**:
- `mu_move_` (line 43): Baseline mean (default: 100.0) - **MUST CALIBRATE**
- `sigma_move_` (line 44): Baseline std dev (default: 20.0) - **MUST CALIBRATE**
- `k_on_` (line 49): ON threshold multiplier (default: 4.0)
- `k_off_` (line 50): OFF threshold multiplier (default: 2.0)

### custom_components/bed_presence_engine/bed_presence.h
**Purpose**: Class definition for BedPresenceEngine
**Lines**: 66 lines
**Inheritance**: `esphome::Component`, `esphome::binary_sensor::BinarySensor`

**Key methods**:
- `setup()`: Initialize component (called once on boot)
- `loop()`: Called every ESPHome cycle (~16ms), processes sensor readings
- `update_k_on(float k)`: Runtime threshold update from HA
- `update_k_off(float k)`: Runtime threshold update from HA
- `process_energy_reading(float energy)`: Core detection logic

**State tracking**:
- `is_occupied_`: Simple boolean (Phase 1 has no state machine)
- `state_reason_`: String showing current z-score for debugging

### packages/presence_engine.yaml
**Purpose**: Defines threshold entities and wiring to C++ component
**Key entities**:
- `binary_sensor.bed_occupied`: Main presence detection output
- `number.k_on_on_threshold_multiplier`: Tunable ON threshold (0-10)
- `number.k_off_off_threshold_multiplier`: Tunable OFF threshold (0-10)
- `text_sensor.presence_state_reason`: Shows z-score values

**Critical configuration**:
```yaml
number:
  - platform: template
    name: "k_on (ON Threshold Multiplier)"
    id: k_on_input
    restore_value: true  # Persists across reboots
    on_value:
      then:
        - lambda: |-
            id(bed_occupied).update_k_on(x);  # Calls C++ method
```

### test/test_presence_engine.cpp
**Purpose**: C++ unit tests for presence detection logic
**Framework**: PlatformIO native testing (GoogleTest style)
**Tests**: 14 test functions covering all Phase 1 behavior

**Test coverage**:
- ✅ Z-score calculation accuracy
- ✅ Initial state (vacant)
- ✅ Occupied detection (z > k_on)
- ✅ Vacant detection (z < k_off)
- ✅ Hysteresis behavior
- ✅ Dynamic threshold updates
- ✅ State reason tracking
- ✅ Edge cases (zero sigma, negative values, large values)

## Development Workflow

### Making Changes to C++ Logic

1. **Read existing tests first**: `test/test_presence_engine.cpp`
   - Understand expected behavior
   - Identify what needs to change

2. **Update/add unit tests**:
   - Modify existing tests if changing behavior
   - Add new tests for new features
   - Run tests: `platformio test -e native`
   - All tests should pass before proceeding

3. **Modify C++ implementation**:
   - Edit `bed_presence.cpp` or `bed_presence.h`
   - Follow ESPHome C++ conventions
   - Add logging with `ESP_LOGD()`, `ESP_LOGI()`, etc.

4. **Compile firmware**:
   ```bash
   esphome compile bed-presence-detector.yaml
   ```
   - Fixes any compilation errors
   - Verifies ESPHome integration

5. **Test with hardware** (if available):
   ```bash
   esphome run bed-presence-detector.yaml
   esphome logs bed-presence-detector.yaml
   ```

### Making Changes to YAML Configuration

1. **Identify the correct package file**:
   - Hardware (GPIO, UART, sensors): `packages/hardware_m5stack_ld2410.yaml`
   - Thresholds/entities: `packages/presence_engine.yaml`
   - Services: `packages/services_calibration.yaml`
   - Diagnostics: `packages/diagnostics.yaml`

2. **Edit the package file**:
   - Follow ESPHome YAML syntax
   - Use 2-space indentation
   - Document non-obvious choices with comments

3. **Validate configuration**:
   ```bash
   esphome config bed-presence-detector.yaml
   ```

4. **Compile to catch integration issues**:
   ```bash
   esphome compile bed-presence-detector.yaml
   ```

5. **Flash and verify** (if changing entities or behavior):
   ```bash
   esphome run bed-presence-detector.yaml
   ```

## C++ Code Style for ESPHome

### Naming Conventions
```cpp
// Classes: CamelCase
class BedPresenceEngine : public Component {

// Private member variables: trailing underscore
private:
  float k_on_;
  bool is_occupied_;

// Public methods: snake_case
public:
  void update_k_on(float k);
  void process_energy_reading(float energy);
};

// Constants: UPPER_CASE or kConstName
const float DEFAULT_K_ON = 4.0f;
static constexpr int kMaxSamples = 1000;
```

### Logging
Use ESPHome logging macros with tags:
```cpp
ESP_LOGD("bed_presence", "Z-score: %.2f, State: %s", z_score, state ? "ON" : "OFF");
ESP_LOGI("bed_presence", "Thresholds updated: k_on=%.1f, k_off=%.1f", k_on_, k_off_);
ESP_LOGW("bed_presence", "Standard deviation is zero, using default");
ESP_LOGE("bed_presence", "Failed to read sensor value");
```

**Log levels**:
- `ESP_LOGD`: Debug info (verbose, only shown in verbose mode)
- `ESP_LOGI`: Informational (state changes, threshold updates)
- `ESP_LOGW`: Warnings (unusual but not critical situations)
- `ESP_LOGE`: Errors (critical failures)

### Memory Management
- Prefer stack allocation for small objects
- Use `std::vector` for dynamic arrays (ESPHome includes STL)
- No raw `new`/`delete` - use RAII or smart pointers if needed
- Be mindful of ESP32 memory constraints (320KB RAM)

### Float Precision
Always use `f` suffix for float literals:
```cpp
float k_on = 4.0f;  // Good
float k_off = 2.0f; // Good
float value = 1.5;  // Bad - this is a double, will be implicitly converted
```

## YAML Configuration Style

### Secrets Management
**CRITICAL**: Use `secrets.yaml` for all sensitive data:
```yaml
# In secrets.yaml (gitignored)
wifi_ssid: "MyNetwork"
wifi_password: "MyPassword123"
api_encryption_key: "base64-key-here"

# In YAML files - reference with !secret
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
```

### Modular Configuration with Packages
The `packages/` directory contains reusable configuration modules:
```yaml
# In bed-presence-detector.yaml
packages:
  hardware: !include packages/hardware_m5stack_ld2410.yaml
  presence: !include packages/presence_engine.yaml
```

**Benefits**:
- Logical separation of concerns
- Easier to test individual subsystems
- Can swap hardware by changing one package file

### Entity Naming
Follow Home Assistant conventions:
```yaml
binary_sensor:
  - platform: bed_presence_engine
    name: "Bed Occupied"              # User-friendly name in HA UI
    id: bed_occupied                  # Internal ESPHome ID (snake_case)

number:
  - platform: template
    name: "k_on (ON Threshold Multiplier)"  # Descriptive name
    id: k_on_input                    # Short ID for lambdas
```

**Entity ID format in HA**: `domain.device_name_entity_name`
- Example: `number.k_on_on_threshold_multiplier`

## Unit Testing Strategy

### SimplePresenceEngine Test Class
The test file defines `SimplePresenceEngine` - a standalone C++ class that replicates Phase 1 logic without ESPHome dependencies:
```cpp
class SimplePresenceEngine {
private:
    float mu_move_ = 100.0f;
    float sigma_move_ = 20.0f;
    float k_on_ = 4.0f;
    float k_off_ = 2.0f;
    bool is_occupied_ = false;

public:
    void process_energy_reading(float energy);
    bool is_occupied() const { return is_occupied_; }
    // ... other methods
};
```

**Why a separate class?**
- ESPHome components can't be easily instantiated in unit tests
- Allows testing core logic in isolation
- No hardware dependencies (runs on development machine)

### Writing New Tests
```cpp
void test_new_feature(void) {
    SimplePresenceEngine engine;
    engine.set_k_on(5.0f);

    // Simulate sensor reading: z = (150 - 100) / 20 = 2.5
    engine.process_energy_reading(150.0f);

    TEST_ASSERT_FALSE(engine.is_occupied());  // Should still be vacant (2.5 < 5.0)
}
```

### Running Tests
```bash
# Run all tests
platformio test -e native

# Run with verbose output
platformio test -e native -v

# List available tests without running
platformio test -e native --list-tests
```

**Expected output** (all passing):
```
test_initial_state_is_vacant: PASS
test_transition_to_occupied_when_energy_exceeds_threshold: PASS
test_transition_to_vacant_when_energy_drops: PASS
test_hysteresis_behavior: PASS
test_no_debouncing: PASS
test_update_k_on_dynamically: PASS
test_update_k_off_dynamically: PASS
test_state_reason_tracking: PASS
test_z_score_calculation_accuracy: PASS
test_zero_standard_deviation: PASS
test_negative_energy_values: PASS
test_very_large_energy_values: PASS
test_thresholds_at_boundaries: PASS
test_multiple_rapid_transitions: PASS
```

## Common Modifications

### Changing Default Thresholds
Update in **two places**:

1. **C++ header** (`bed_presence.h:49-50`):
```cpp
float k_on_{4.0f};   // Default ON threshold
float k_off_{2.0f};  // Default OFF threshold
```

2. **YAML config** (`packages/presence_engine.yaml:24, 40`):
```yaml
number:
  - platform: template
    name: "k_on (ON Threshold Multiplier)"
    initial_value: 4.0  # Must match C++ default

  - platform: template
    name: "k_off (OFF Threshold Multiplier)"
    initial_value: 2.0  # Must match C++ default
```

**Why both?** C++ provides compile-time default, YAML provides runtime initial value for Home Assistant entity.

### Updating Baseline Statistics (Manual Calibration)
After collecting baseline data from hardware (see `../docs/phase1-hardware-setup.md`):

1. Calculate mean (μ) and standard deviation (σ) from empty bed readings
2. Update in `bed_presence.h:43-46`:
```cpp
// OLD (placeholder values)
float mu_move_{100.0f};
float sigma_move_{20.0f};

// NEW (from your calibration data)
float mu_move_{87.3f};    // Your calculated mean
float sigma_move_{15.8f}; // Your calculated std dev
```
3. Recompile and reflash: `esphome run bed-presence-detector.yaml`

### Adding New Sensor Entities
To expose new data to Home Assistant:

1. **Add to appropriate package file** (e.g., `packages/diagnostics.yaml`):
```yaml
sensor:
  - platform: template
    name: "Z-Score Value"
    id: z_score_sensor
    unit_of_measurement: "σ"
    accuracy_decimals: 2
    update_interval: 1s
```

2. **Update C++ to publish value**:
```cpp
// In bed_presence.cpp, after calculating z_score
if (z_score_sensor_ != nullptr) {
  z_score_sensor_->publish_state(z_score);
}
```

3. **Add pointer in header** (`bed_presence.h`):
```cpp
sensor::Sensor *z_score_sensor_{nullptr};
```

4. **Wire in component registration** (`binary_sensor.py` or `__init__.py`)

### Changing Hardware Configuration
To use different GPIO pins or UART settings, edit `packages/hardware_m5stack_ld2410.yaml`:

```yaml
uart:
  id: ld2410_uart
  tx_pin: GPIO17  # Change these for your board
  rx_pin: GPIO16
  baud_rate: 256000  # LD2410 requires 256000 baud

ld2410:
  uart_id: ld2410_uart
  # ... rest of LD2410 configuration
```

**Common ESP32 boards**:
- **M5Stack Basic**: TX=GPIO17, RX=GPIO16 (default in this project)
- **ESP32 DevKit**: TX=GPIO17, RX=GPIO16 (same as M5Stack)
- **ESP32-C3**: Check your specific board's pinout

## Integration with ESPHome Ecosystem

### Component Lifecycle
ESPHome calls these methods in order:
1. `setup()`: Called once on boot - initialize variables, register callbacks
2. `loop()`: Called every ~16ms - check sensors, update state
3. `dump_config()`: Called during startup - log configuration to console

**Phase 1 implementation**:
```cpp
void BedPresenceEngine::setup() {
  ESP_LOGCONFIG("bed_presence", "Bed Presence Engine initialized");
  ESP_LOGCONFIG("bed_presence", "  k_on: %.2f", k_on_);
  ESP_LOGCONFIG("bed_presence", "  k_off: %.2f", k_off_);
}

void BedPresenceEngine::loop() {
  // Read sensor value
  if (energy_sensor_ && energy_sensor_->has_state()) {
    float energy = energy_sensor_->state;
    process_energy_reading(energy);
  }
}
```

### Sensor Value Updates
Two approaches:

**Polling (current implementation)**:
```cpp
void loop() {
  if (sensor_->has_state()) {
    float value = sensor_->state;
    // Process value
  }
}
```

**Callback (more efficient)**:
```cpp
void setup() {
  sensor_->add_on_state_callback([this](float value) {
    process_energy_reading(value);
  });
}
```

### Publishing State to Home Assistant
```cpp
// Binary sensor (ON/OFF)
this->publish_state(true);  // Occupied
this->publish_state(false); // Vacant

// Text sensor (strings)
state_reason_sensor_->publish_state("z=4.2 > k_on=4.0 (occupied)");

// Number sensor (values)
z_score_sensor_->publish_state(4.23f);
```

## Debugging & Troubleshooting

### Viewing Logs
**Over USB serial**:
```bash
esphome logs bed-presence-detector.yaml
```

**Over WiFi** (after initial flash):
```bash
esphome logs bed-presence-detector.yaml --device bed-presence-detector.local
```

**In Home Assistant**:
Settings → Devices & Services → ESPHome → [Device] → Logs

### Common Compile Errors

**"undefined reference to ESPHome function"**
- **Cause**: Missing ESPHome includes in C++ files
- **Fix**: Add `#include "esphome/core/component.h"` or relevant header

**"'binary_sensor::BinarySensor' has not been declared"**
- **Cause**: Missing namespace or forward declaration
- **Fix**: Add `#include "esphome/components/binary_sensor/binary_sensor.h"`

**"expected unqualified-id before 'float'"**
- **Cause**: Syntax error in C++ (missing semicolon, brace, etc.)
- **Fix**: Check line number in error message, verify syntax

### Common Runtime Issues

**Sensor always reports vacant**
- **Check**: Are baseline values (`mu_move_`, `sigma_move_`) correct for your environment?
- **Debug**: Add logging in `process_energy_reading()` to see z-scores
- **Fix**: Perform manual calibration (see `../docs/phase1-hardware-setup.md`)

**Sensor is too sensitive ("twitchy")**
- **Expected**: Phase 1 has no debouncing (immediate state changes)
- **Temporary fix**: Increase `k_on` threshold or widen hysteresis gap
- **Permanent fix**: Implement Phase 2 state machine with debounce timers

**"Component took a long time for an operation"**
- **Cause**: `loop()` method taking too long (>100ms)
- **Fix**: Move expensive operations out of `loop()` or add `yield()` calls
- **Check**: Are you doing blocking I/O or heavy computation in `loop()`?

### Debugging Z-Score Calculation
Add verbose logging:
```cpp
void process_energy_reading(float energy) {
  float z_score = (energy - mu_move_) / sigma_move_;

  ESP_LOGD("bed_presence", "Raw energy: %.1f", energy);
  ESP_LOGD("bed_presence", "Baseline: μ=%.1f, σ=%.1f", mu_move_, sigma_move_);
  ESP_LOGD("bed_presence", "Z-score: %.2f (k_on=%.1f, k_off=%.1f)",
           z_score, k_on_, k_off_);
  ESP_LOGD("bed_presence", "Current state: %s", is_occupied_ ? "OCCUPIED" : "VACANT");

  // ... rest of logic
}
```

Enable verbose logging in YAML:
```yaml
logger:
  level: VERBOSE  # Shows ESP_LOGD messages
```

## Phase-Specific Implementation Notes

### Phase 1 (Current)
**What exists**:
- Simple boolean state (`is_occupied_`)
- Z-score calculation with hysteresis
- Runtime tunable thresholds
- Hardcoded baseline statistics

**What's intentionally missing**:
- ❌ State machine enum (just boolean state)
- ❌ Debounce timers (immediate transitions)
- ❌ Temporal filtering
- ❌ Automated calibration

**Don't add Phase 2/3 features unless explicitly implementing those phases!**

### Phase 2 (Planned)
**Required changes** (see `../docs/presence-engine-spec.md` Phase 2):
- Add state machine enum: `IDLE`, `DEBOUNCING_ON`, `PRESENT`, `DEBOUNCING_OFF`
- Add timer tracking: `unsigned long last_state_change_time_`
- Add debounce parameters: `debounce_on_ms_`, `debounce_off_ms_`
- Refactor `process_energy_reading()` to implement state machine logic
- Add debounce timer entities to `packages/presence_engine.yaml`

**Testing requirements**:
- Mock time in unit tests
- Test all state transitions
- Test timer expiration logic
- Verify debounce prevents false positives/negatives

### Phase 3 (Planned)
**Required changes** (see `../docs/presence-engine-spec.md` Phase 3):
- Implement calibration services in `packages/services_calibration.yaml`
- Add data collection mode: `bool is_calibrating_`
- Store samples: `std::vector<float> calibration_samples_`
- Implement MAD statistical calculation
- Add distance windowing logic
- Create calibration wizard UI

## Hardware-Specific Notes

### LD2410 mmWave Sensor
**Communication**: UART at 256000 baud
**Update rate**: ~10Hz (new readings every 100ms)
**Key sensors**:
- `ld2410_still_energy`: Stationary target energy (0-100, used by Phase 1)
- `ld2410_moving_energy`: Moving target energy (0-100, reserved for future use)
- `ld2410_detection_distance`: Distance to detected target in cm

**Phase 1 uses only** `ld2410_still_energy` sensor.

### M5Stack Basic v2.7
**Microcontroller**: ESP32-PICO-D4 (dual-core, 4MB flash)
**GPIO**: Available pins for UART on internal header
**Power**: USB-C (5V) or battery (not included)
**Display**: 320x240 TFT (not used by this project currently)

**Important**: If using different ESP32 board, verify GPIO pin availability.

## Quick Reference for Common Tasks

| Task | Command | Notes |
|------|---------|-------|
| Compile firmware | `esphome compile bed-presence-detector.yaml` | Validates YAML + C++ |
| Run unit tests | `platformio test -e native` | 14 tests, ~5 seconds |
| Flash device | `esphome run bed-presence-detector.yaml` | Requires USB connection |
| View logs | `esphome logs bed-presence-detector.yaml` | Real-time log streaming |
| Validate YAML | `esphome config bed-presence-detector.yaml` | Quick syntax check |
| Clean build | `esphome clean bed-presence-detector.yaml` | Removes cached files |

## Additional Resources

- **ESPHome Documentation**: https://esphome.io/
- **LD2410 Component Docs**: https://esphome.io/components/sensor/ld2410.html
- **ESPHome Custom Components Guide**: https://esphome.io/custom/custom_component.html
- **PlatformIO Unit Testing**: https://docs.platformio.org/en/latest/advanced/unit-testing/
- **ESP32 Datasheet**: Search for "ESP32-PICO-D4 datasheet"

---

**Need broader context?** See `../CLAUDE.md` for comprehensive project documentation, or `../AGENTS.md` for repository-wide agent guidance.
