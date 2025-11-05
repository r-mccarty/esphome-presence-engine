# AGENTS.md - Home Assistant Configuration

This file provides guidance for AI agents working with Home Assistant configuration files in this directory.

## Overview

This directory contains Home Assistant configuration artifacts for the bed presence detection system. These files are designed to be copied into a Home Assistant instance, NOT run directly from this repository.

**Important**: This is NOT a complete Home Assistant configuration directory. These are **supplementary files** that users add to their existing Home Assistant setup.

## Directory Structure

```
homeassistant/
├── blueprints/
│   └── automation/
│       └── bed_presence_automation.yaml    # Automation blueprint for presence triggers
├── dashboards/
│   └── bed_presence_dashboard.yaml         # Lovelace UI dashboard
└── configuration_helpers.yaml.example       # Helper entity definitions (template)
```

## File Purposes

### blueprints/automation/bed_presence_automation.yaml
**Type**: Home Assistant Automation Blueprint
**Purpose**: Provides a reusable automation template for presence-triggered actions
**User workflow**: Copy to `<ha_config>/blueprints/automation/` → Create automation from blueprint in HA UI

**What it does**:
- Triggers when `binary_sensor.bed_occupied` changes state
- Allows user to select actions for "occupied" and "vacant" events
- Optional person presence filtering
- Optional time window restrictions

**Example use cases**:
- Turn off bedroom lights when bed becomes occupied
- Send notification when bed has been vacant for >1 hour (wake-up detection)
- Adjust thermostat when person enters/exits bed
- Trigger sleep tracking routine

### dashboards/bed_presence_dashboard.yaml
**Type**: Lovelace Dashboard Configuration (YAML mode)
**Purpose**: Provides a complete UI for monitoring and configuring the bed presence sensor
**User workflow**: Create new dashboard in HA → Edit → Raw Configuration Editor → Paste YAML

**Dashboard views**:
1. **Status View**: Real-time presence state, energy readings, z-score visualization
2. **Configuration View**: Tune `k_on` and `k_off` thresholds via sliders
3. **Diagnostics View**: WiFi signal, uptime, ESPHome version, device info

**Current status**: ✅ **Phase 1 complete** - All entity names match Phase 1 implementation

**Phase 1 entity references**:
- `binary_sensor.bed_occupied`: Main presence state
- `number.k_on_on_threshold_multiplier`: ON threshold slider (0-10)
- `number.k_off_off_threshold_multiplier`: OFF threshold slider (0-10)
- `text_sensor.presence_state_reason`: Shows z-score values for debugging
- `sensor.ld2410_still_energy`: Raw sensor reading (0-100)

**Commented-out sections** (Phase 3 features):
- Calibration Wizard view (requires helper entities not yet implemented)
- Helper entity definitions are in `configuration_helpers.yaml.example`

### configuration_helpers.yaml.example
**Type**: Template for helper entity definitions
**Purpose**: Documents helper entities needed for Phase 3 calibration wizard
**User workflow**: Copy contents to `<ha_config>/configuration.yaml` (when Phase 3 is implemented)

**Helper entities** (Phase 3 - not yet functional):
- `input_boolean.bed_presence_calibrating`: Tracks calibration mode state
- `input_number.calibration_duration`: Calibration time in seconds (30-300)
- `input_text.calibration_status`: Status message during calibration

**Current status**: ⚠️ **Placeholder only** - These entities are not used in Phase 1

## Phase 1 Implementation Status

### What Works Now
✅ **Status View**: Fully functional
- Shows real-time presence state
- Displays raw sensor energy readings
- Shows z-score values in state reason text sensor

✅ **Configuration View**: Fully functional
- Adjust `k_on` threshold (default: 4.0)
- Adjust `k_off` threshold (default: 2.0)
- Changes take effect immediately without reflashing device

✅ **Diagnostics View**: Fully functional
- WiFi signal strength
- Device uptime
- ESPHome version
- IP address

✅ **Automation Blueprint**: Fully functional
- Triggers on presence state changes
- Supports basic automation patterns

### What Doesn't Work Yet
❌ **Calibration Wizard** (Phase 3 feature)
- View is commented out in `bed_presence_dashboard.yaml`
- Helper entities defined in `configuration_helpers.yaml.example` but not used
- Services exist in ESPHome but only log messages (no actual calibration)

❌ **Debounce Timer Controls** (Phase 2 feature)
- Not present in Phase 1 (intentionally)
- Phase 2 will add debounce timer sliders to Configuration view

## Deploying to Home Assistant

### Dashboard Deployment

**Prerequisites**:
- Home Assistant instance running (version 2023.1 or later recommended)
- ESPHome integration installed
- Bed presence detector device connected and showing entities

**Steps**:
1. In Home Assistant web UI: Settings → Dashboards → Add Dashboard
2. Click "Create new dashboard"
3. Give it a name (e.g., "Bed Presence Monitor")
4. Click the pencil icon (Edit Dashboard)
5. Click "⋮" menu → "Raw configuration editor"
6. Copy entire contents of `bed_presence_dashboard.yaml`
7. Paste into the editor
8. Click "Save"
9. Exit edit mode

**Verification**:
- Navigate to the new dashboard
- You should see Status, Configuration, and Diagnostics views
- All entities should show data (no "Unknown" or "Unavailable")
- Threshold sliders should be interactive

**Troubleshooting**:
- **"Entity not found" errors**: Verify ESPHome device is connected and entities exist
- **"Invalid YAML" errors**: Check for copy/paste corruption, verify indentation
- **Empty charts**: Wait a few minutes for history data to accumulate

### Automation Blueprint Deployment

**Method 1: File Copy** (Recommended)
1. Access your Home Assistant configuration directory (via Samba, SSH, or File Editor add-on)
2. Navigate to `blueprints/automation/` (create directories if they don't exist)
3. Copy `bed_presence_automation.yaml` to that directory
4. Restart Home Assistant (Settings → System → Restart) OR Developer Tools → YAML → Reload Automations

**Method 2: Blueprint Import** (If blueprint becomes public)
```
# Future: When hosted on GitHub
Settings → Automations & Scenes → Blueprints → Import Blueprint
URL: https://github.com/r-mccarty/bed-presence-sensor/blueprints/automation/bed_presence_automation.yaml
```

**Using the Blueprint**:
1. Settings → Automations & Scenes → Create Automation
2. Click "Start with a blueprint"
3. Find "Bed Presence Triggered Actions" blueprint
4. Fill in:
   - **Bed Presence Sensor**: Select `binary_sensor.bed_occupied`
   - **Actions when occupied**: Add actions (turn off lights, etc.)
   - **Actions when vacant**: Add actions (turn on lights, etc.)
   - *Optional*: Set person presence filter or time restrictions
5. Give automation a name and save

### Helper Entities (Phase 3 Only)

**Current status**: Not needed for Phase 1

**When Phase 3 is implemented**:
1. Open Home Assistant configuration file (`configuration.yaml`)
2. Add contents of `configuration_helpers.yaml.example`
3. Restart Home Assistant
4. Verify entities exist: Developer Tools → States → Search for "bed_presence_calibrating"

## Modifying Dashboard Configuration

### Entity Names in Phase 1
**CRITICAL**: Always use these entity names (generated by ESPHome device):

```yaml
# Binary sensor (presence state)
binary_sensor.bed_occupied

# Number inputs (thresholds)
number.k_on_on_threshold_multiplier     # ON threshold (default: 4.0)
number.k_off_off_threshold_multiplier   # OFF threshold (default: 2.0)

# Text sensors
text_sensor.presence_state_reason       # Shows z-score values

# Sensors from LD2410
sensor.ld2410_still_energy              # Raw energy reading (0-100)
sensor.ld2410_moving_energy             # (Not used in Phase 1)
sensor.ld2410_detection_distance        # Distance in cm

# Diagnostics
sensor.wifi_signal_sensor               # WiFi signal strength (dBm)
sensor.uptime                           # Device uptime
text_sensor.esphome_version             # ESPHome version string
text_sensor.ip_address                  # Device IP address
```

**Note**: Entity names are prefixed with device name by Home Assistant. If you named your device something other than default, adjust entity IDs accordingly.

### Adding New Cards to Dashboard

Example: Add a history graph for z-score values

```yaml
# Add to one of the views in bed_presence_dashboard.yaml
- type: history-graph
  title: Z-Score History
  hours_to_show: 2
  entities:
    - entity: text_sensor.presence_state_reason
      name: State Reason
```

### Customizing Threshold Ranges

To change the min/max values for threshold sliders:

**In ESPHome configuration** (`../esphome/packages/presence_engine.yaml`):
```yaml
number:
  - platform: template
    name: "k_on (ON Threshold Multiplier)"
    min_value: 0.0    # Change minimum
    max_value: 10.0   # Change maximum
    step: 0.1         # Slider step size
```

**In Dashboard** (`dashboards/bed_presence_dashboard.yaml`):
```yaml
# The dashboard automatically respects min/max from entity definition
- type: entities
  entities:
    - entity: number.k_on_on_threshold_multiplier
      # No need to specify range here - inherited from entity
```

### Adding Phase 2 Debounce Controls (When Implementing)

When Phase 2 is implemented, add to Configuration view:

```yaml
- type: entities
  title: Debounce Timers
  entities:
    - entity: number.debounce_on_ms
      name: "Occupied Debounce (ms)"
      icon: mdi:timer-sand
    - entity: number.debounce_off_ms
      name: "Vacant Debounce (ms)"
      icon: mdi:timer-sand
    - entity: number.abs_clear_delay_ms
      name: "Absolute Clear Delay (ms)"
      icon: mdi:timer-alert
```

**Remember**: Also add these entities to ESPHome configuration!

## Automation Blueprint Customization

### Blueprint Structure

```yaml
blueprint:
  name: Bed Presence Triggered Actions
  description: "Triggers actions based on bed occupancy state"
  domain: automation
  input:
    bed_sensor:
      name: Bed Presence Sensor
      selector:
        entity:
          domain: binary_sensor
    # ... more inputs

trigger:
  - platform: state
    entity_id: !input bed_sensor
    # ... trigger configuration

action:
  - choose:
      - conditions:
          - condition: state
            entity_id: !input bed_sensor
            state: "on"
        sequence: !input occupied_actions
      - conditions:
          - condition: state
            entity_id: !input bed_sensor
            state: "off"
        sequence: !input vacant_actions
```

### Adding New Blueprint Inputs

Example: Add a "morning time" filter

```yaml
blueprint:
  input:
    # ... existing inputs
    morning_time:
      name: Morning Time
      description: Only trigger vacant actions after this time
      selector:
        time:
      default: "06:00:00"

action:
  - choose:
      - conditions:
          - condition: state
            entity_id: !input bed_sensor
            state: "off"
          - condition: time
            after: !input morning_time  # Use the input
        sequence: !input vacant_actions
```

### Common Automation Patterns

**Turn off lights when bed becomes occupied**:
```yaml
# In automation created from blueprint
occupied_actions:
  - service: light.turn_off
    target:
      entity_id: light.bedroom_lights
    data:
      transition: 2  # Fade out over 2 seconds
```

**Send notification when waking up**:
```yaml
# In automation created from blueprint
vacant_actions:
  - condition: time
    after: "06:00:00"
    before: "10:00:00"
  - service: notify.mobile_app
    data:
      message: "Good morning! You've been awake for {{ trigger.to_state.state_duration }} seconds"
```

**Adjust thermostat based on presence**:
```yaml
occupied_actions:
  - service: climate.set_temperature
    target:
      entity_id: climate.bedroom_thermostat
    data:
      temperature: 68  # Sleep temperature

vacant_actions:
  - service: climate.set_temperature
    target:
      entity_id: climate.bedroom_thermostat
    data:
      temperature: 70  # Wake temperature
```

## Home Assistant Version Compatibility

**Minimum version**: 2023.1 (for latest blueprint selector features)
**Recommended version**: 2024.1 or later
**Tested on**: 2024.11 (latest at time of Phase 1 completion)

**Breaking changes to watch for**:
- Dashboard YAML syntax (rarely changes, but check HA release notes)
- Blueprint selector syntax (stable since 2023.1)
- ESPHome integration API (stable across versions)

## Lovelace Card Types Used

### Status View
- `entities` card: Displays list of entities with values
- `history-graph` card: Shows time-series data
- `gauge` card: Visual indicator for energy levels (0-100 range)
- `markdown` card: Instructions and explanations

### Configuration View
- `entities` card: Threshold sliders and settings
- `markdown` card: Usage instructions

### Diagnostics View
- `entities` card: Device information
- `glance` card: Quick overview of multiple sensors

**All card types are built-in** to Home Assistant - no custom cards required.

## Testing Dashboard Changes

### Testing Locally Before Deployment

1. **YAML Validation**: Use online YAML validator (e.g., yamllint.com)
   - Paste dashboard YAML
   - Check for syntax errors

2. **Entity Verification**: Check entities exist in your HA instance
   - Developer Tools → States → Search for entity IDs
   - Verify entity IDs match dashboard YAML

3. **Test Dashboard**: Create test dashboard first
   - Settings → Dashboards → Add Dashboard
   - Paste modified YAML
   - Verify functionality
   - If good, apply to production dashboard

### Common Dashboard Errors

**"Entity not available"**
- **Cause**: Entity ID doesn't match device's actual entities
- **Fix**: Go to Settings → Devices & Services → ESPHome → [Device] → See all entities
- **Verify**: Copy exact entity ID from there

**"Custom element doesn't exist"**
- **Cause**: Trying to use custom card that's not installed
- **Fix**: This project uses only built-in cards, verify no typos in `type:` field

**Charts show no data**
- **Cause**: No history data yet (fresh installation)
- **Fix**: Wait 5-10 minutes for Home Assistant recorder to collect data
- **Verify**: Check Settings → System → Repairs for recorder errors

## Integration with Home Assistant Ecosystem

### Home Assistant Recorder
The dashboard's history graphs require the **Recorder** integration (enabled by default).

**Configuration** (`configuration.yaml` on HA instance):
```yaml
recorder:
  db_url: sqlite:///home-assistant_v2.db  # Default
  purge_keep_days: 7  # How long to keep history (adjust as needed)
  include:
    entities:
      - binary_sensor.bed_occupied
      - sensor.ld2410_still_energy
      - number.k_on_on_threshold_multiplier
      - number.k_off_off_threshold_multiplier
```

**Note**: Explicit `include` is optional - by default, recorder tracks all entities.

### Home Assistant Energy Dashboard
The bed presence sensor is **not** an energy monitoring device (despite using "energy" readings from LD2410).

The LD2410 "energy" values represent **signal energy** (radio waves), not electrical energy consumption.

### Home Assistant Mobile App
Dashboard is fully compatible with Home Assistant mobile app:
- Status view shows current state and diagnostics
- Configuration sliders work on mobile
- Automation notifications work via mobile app service

**Mobile-specific considerations**:
- Gauge cards render well on small screens
- History graphs may be cramped on phone screens
- Consider creating a simplified "mobile view" if needed

## Security Considerations

### No Sensitive Data
These configuration files contain **no secrets**:
- ✅ Entity IDs (public within your HA instance)
- ✅ Automation logic (no credentials)
- ✅ Dashboard layout (cosmetic only)

### ESPHome Device Security
Security is handled at the **ESPHome device level**:
- API encryption key (in `../esphome/secrets.yaml` on device)
- OTA password (in `../esphome/secrets.yaml` on device)
- WiFi credentials (in `../esphome/secrets.yaml` on device)

**Home Assistant configuration files do not contain these secrets.**

### Blueprint Security
Blueprints can execute arbitrary actions - only use blueprints from trusted sources.

**This blueprint**:
- ✅ Open source (inspect code before use)
- ✅ No network calls (only local HA actions)
- ✅ User-controlled actions (you choose what it does)

## Phase-Specific Notes

### Phase 1 (Current)
**Available now**:
- ✅ Status monitoring dashboard
- ✅ Threshold configuration UI
- ✅ Basic automation blueprint
- ✅ Diagnostics view

**Not available yet**:
- ❌ Calibration wizard UI (Phase 3)
- ❌ Debounce timer controls (Phase 2)
- ❌ Distance windowing UI (Phase 3)

### Phase 2 (Planned)
**Will add**:
- Debounce timer sliders to Configuration view
- State machine state display (IDLE, DEBOUNCING_ON, PRESENT, DEBOUNCING_OFF)
- Temporal filtering statistics

**Dashboard changes required**:
- Add entities to Configuration view for debounce timers
- Update Status view to show state machine state

### Phase 3 (Planned)
**Will add**:
- Calibration wizard view (currently commented out)
- Helper entities for calibration workflow
- Distance windowing controls
- MAD statistics display

**Dashboard changes required**:
- Uncomment Calibration Wizard view in `bed_presence_dashboard.yaml`
- Add helper entities from `configuration_helpers.yaml.example` to HA config
- Wire calibration UI to ESPHome services

## Troubleshooting Checklist

Before asking for help or debugging:

- [ ] ESPHome device is online and connected to Home Assistant
- [ ] Device appears in Settings → Devices & Services → ESPHome
- [ ] All expected entities are present (check device page)
- [ ] Entity IDs in dashboard YAML match actual entity IDs
- [ ] Dashboard YAML syntax is valid (no YAML errors on save)
- [ ] Home Assistant Recorder is enabled (for history graphs)
- [ ] Waited at least 5 minutes after fresh install (for history data)
- [ ] Checked Home Assistant logs: Settings → System → Logs
- [ ] Checked ESPHome device logs: Device page → Logs button

## Additional Resources

- **Lovelace Documentation**: https://www.home-assistant.io/lovelace/
- **Blueprint Documentation**: https://www.home-assistant.io/docs/automation/using_blueprints/
- **Home Assistant Automation**: https://www.home-assistant.io/docs/automation/
- **ESPHome Integration**: https://www.home-assistant.io/integrations/esphome/
- **Entity Customization**: https://www.home-assistant.io/docs/configuration/customizing-devices/

---

**Need broader context?** See `../CLAUDE.md` for comprehensive project documentation, or `../AGENTS.md` for repository-wide agent guidance.
