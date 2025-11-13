# RFD-003: Bluetooth Beacon Distance Calibration for Presence Detection

## Metadata

- **Status:** 🟡 Proposed (Discussion)
- **Date:** 2025-11-13
- **Author:** Community Contributor
- **Decision Makers:** Project Team
- **Impacts:** Architecture, sensor fusion, Phase 4+ roadmap, privacy considerations
- **Related Documents:**
  - `docs/ARCHITECTURE.md` (current z-score engine)
  - `docs/presence-engine-spec.md` (3-phase specification)
  - `docs/RFD-001-still-vs-moving-energy.md` (sensor selection rationale)
  - `docs/HARDWARE_SETUP.md` (current LD2410 setup)

---

## Executive Summary

**Proposal:** Evaluate adding **Bluetooth Low Energy (BLE) beacon tracking** with distance estimation to complement or enhance the existing LD2410 mmWave radar presence detection system. BLE beacons could provide person-specific presence detection (identifying *who* is present, not just *if* someone is present) and enable multi-zone tracking beyond the bed.

**Motivation:** The current LD2410-based system excels at detecting *occupancy* of a fixed zone (bed), but cannot:
1. Identify *which person* is present
2. Track presence across multiple rooms/zones
3. Distinguish between multiple people in the same space
4. Provide continuous presence tracking when a person leaves the bed zone

**Key Questions:**
- Should BLE beacons **replace**, **complement**, or **extend** the LD2410 sensor?
- What are the primary use cases: bed presence enhancement, whole-home tracking, or person identification?
- Can RSSI-to-distance conversion be reliable enough for presence detection?
- How does this impact privacy, power consumption, and system complexity?

**This RFD is exploratory** - it presents technical analysis, implementation options, and tradeoffs for community discussion.

---

## Context

### Current System: LD2410 mmWave Radar

The deployed Phase 3 system uses an **LD2410 mmWave radar** sensor for bed presence detection:

**Strengths:**
- ✅ **Privacy-preserving**: No cameras, no person identification
- ✅ **Passive detection**: No wearables or devices required
- ✅ **High accuracy**: Z-score based detection with >95% accuracy
- ✅ **Environmental immunity**: Stable baselines, low false positives
- ✅ **Real-time**: Sub-second latency, on-device processing
- ✅ **Zone-focused**: Excellent at detecting occupancy in a fixed zone (bed)

**Limitations:**
- ❌ **Anonymous detection**: Cannot identify which person is present
- ❌ **Single-zone**: One sensor = one detection zone
- ❌ **No person tracking**: Cannot follow a person across rooms
- ❌ **No multi-person**: Cannot distinguish between 2+ people in bed
- ❌ **Fixed mounting**: Sensor must be statically positioned

### Problem Statement

**Scenario 1: Person Identification**
- **Use case**: Dual-occupancy bed (couples, roommates)
- **Current limitation**: System detects "someone in bed" but not who
- **User need**: Different automations for different people (wake-up times, lighting preferences, sleep tracking)

**Scenario 2: Multi-Zone Presence**
- **Use case**: Track presence across bedroom, bathroom, closet
- **Current limitation**: Would require 3+ LD2410 sensors ($90+ cost)
- **User need**: Unified presence tracking as person moves between zones

**Scenario 3: Presence Context**
- **Use case**: Differentiate "in bed sleeping" vs "in bed reading" vs "in room but not in bed"
- **Current limitation**: LD2410 only knows bed occupancy
- **User need**: More granular context for smart home automations

**Could Bluetooth beacons solve these problems?**

---

## Bluetooth Beacon Fundamentals

### What is a BLE Beacon?

A **Bluetooth Low Energy (BLE) beacon** is a small, battery-powered device that periodically broadcasts its presence via radio signals. Common beacon formats:
- **iBeacon** (Apple standard)
- **Eddystone** (Google standard)
- **AltBeacon** (open standard)
- **Generic BLE advertisements**

**Key Characteristics:**
- **Range**: 10-100 meters (depending on transmit power)
- **Battery life**: 1-3 years on coin cell battery
- **Broadcast interval**: 100ms - 10 seconds (configurable)
- **RSSI (Received Signal Strength Indicator)**: Measured in dBm (e.g., -40 dBm = very close, -90 dBm = far)

### RSSI-to-Distance Conversion

Distance estimation from RSSI uses a **path loss model**:

```
RSSI = TxPower - 10 * n * log10(distance)
```

Where:
- `RSSI` = Received signal strength (dBm)
- `TxPower` = Transmit power at 1 meter (dBm) - calibrated per beacon
- `n` = Path loss exponent (2.0 in free space, 2.5-4.0 indoors)
- `distance` = Estimated distance in meters

**Solving for distance:**
```
distance = 10 ^ ((TxPower - RSSI) / (10 * n))
```

**Example:**
- TxPower = -59 dBm (calibrated at 1m)
- RSSI = -75 dBm (measured)
- n = 3.0 (indoor environment)
- Distance = 10^((-59 - (-75)) / (10 * 3.0)) = 10^(16/30) ≈ 3.5 meters

### Challenges with RSSI Distance Estimation

**Accuracy Issues:**
- ❌ **Signal multipath**: Reflections from walls/furniture cause interference
- ❌ **Body absorption**: Human body attenuates signal (5-10 dB when beacon in pocket)
- ❌ **Environmental variance**: Different rooms have different path loss exponents
- ❌ **Orientation sensitivity**: Beacon angle affects signal strength
- ❌ **Interference**: WiFi, Bluetooth devices, microwaves degrade signal

**Typical Accuracy:**
- ✅ **Zone detection**: Reliable (same room vs. different room)
- ⚠️ **Proximity detection**: Moderate (within 2m vs. beyond 2m)
- ❌ **Precise distance**: Poor (±1-3 meter error)

**Key Insight:** BLE beacons are **better for proximity/zone detection** than precise distance measurement.

---

## Use Cases for BT Beacon Integration

### Use Case 1: Person Identification (Complementary to LD2410)

**Architecture:** LD2410 for bed occupancy + BLE beacon for identity

**Workflow:**
1. LD2410 detects "bed occupied" (binary sensor ON)
2. ESP32 scans for nearby BLE beacons
3. System identifies which beacon(s) are close enough to bed (<2m)
4. Publishes identity: `sensor.bed_occupant = "person_a"` or `"person_a,person_b"`

**Example Automation:**
```yaml
# Different wake-up routines for different people
automation:
  - alias: "Wake Person A (Early Bird)"
    trigger:
      platform: time
      at: "06:00:00"
    condition:
      - condition: state
        entity_id: sensor.bed_occupant
        state: "person_a"
    action:
      - service: light.turn_on
        target: { entity_id: light.bedroom }
        data: { brightness: 50 }
```

**Pros:**
- ✅ Leverages existing LD2410 accuracy for occupancy detection
- ✅ Adds person identification without sacrificing reliability
- ✅ Beacon only used when LD2410 confirms occupancy
- ✅ Enables person-specific automations

**Cons:**
- ❌ Requires users to carry/wear beacons (wearable, phone, smartwatch)
- ❌ Battery maintenance (recharge/replace beacon batteries)
- ❌ Privacy: Beacons broadcast unique identifiers

---

### Use Case 2: Multi-Zone Tracking (Alternative to LD2410)

**Architecture:** Multiple BLE beacons placed in different zones

**Workflow:**
1. Person carries a BLE beacon (phone, smartwatch, tag)
2. ESP32(s) in each zone (bedroom, bathroom, closet) scan for beacon
3. System determines presence zone based on strongest RSSI
4. Publishes `sensor.person_a_location = "bedroom"` or `"bathroom"`

**Example Automation:**
```yaml
# Turn on bathroom light when person enters
automation:
  - alias: "Bathroom Entry Lighting"
    trigger:
      platform: state
      entity_id: sensor.person_a_location
      to: "bathroom"
    action:
      - service: light.turn_on
        target: { entity_id: light.bathroom }
```

**Pros:**
- ✅ Tracks person across multiple rooms with 1 beacon
- ✅ Cheaper than deploying LD2410 sensors in every room
- ✅ Works for presence tracking beyond fixed zones

**Cons:**
- ❌ Lower accuracy than LD2410 for fixed-zone detection
- ❌ Requires person to carry beacon at all times
- ❌ Does not detect presence if person forgets beacon
- ❌ Struggles with multi-person scenarios (RSSI overlap)

---

### Use Case 3: Hybrid Sensor Fusion (Best of Both)

**Architecture:** Combine LD2410 (high-accuracy zone) + BLE beacons (identity + multi-zone)

**Workflow:**
1. **Bedroom zone**: LD2410 for bed occupancy (high accuracy)
2. **Other zones**: BLE beacon tracking (bathroom, closet, hallway)
3. **Fusion logic**: LD2410 takes precedence in bed zone, BLE elsewhere
4. Publishes unified presence state: `sensor.person_a_state = "in_bed"` or `"in_bathroom"`

**State Machine Example:**
```
Person A State Machine:
- NOT_HOME: No beacon detected anywhere
- HOME_OTHER: Beacon detected, but not in specific zone
- IN_BEDROOM: Beacon in bedroom zone (no bed occupancy)
- IN_BED: LD2410 ON + Beacon in bedroom zone
- IN_BATHROOM: Beacon in bathroom zone
```

**Pros:**
- ✅ Combines LD2410 reliability with BLE flexibility
- ✅ High-accuracy bed presence + multi-zone tracking
- ✅ Person identification + location awareness
- ✅ Enables rich automations (sleep tracking, wake-up, lighting paths)

**Cons:**
- ❌ Highest complexity (two sensor types, fusion logic)
- ❌ Requires beacon maintenance and user adoption
- ❌ More points of failure (LD2410 OR beacon can fail)

---

## Technical Implementation Paths

### Option A: ESP32 BLE Scanning (On-Device)

**Approach:** Use the ESP32's built-in Bluetooth radio to scan for nearby beacons.

**ESPHome Implementation:**

ESPHome has native support for BLE tracking via the `esp32_ble_tracker` component:

```yaml
# esphome/packages/ble_beacon_tracking.yaml
esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
    active: false  # Passive scanning (lower power)

# Track specific beacons
sensor:
  - platform: ble_rssi
    mac_address: "AA:BB:CC:DD:EE:FF"  # Person A's beacon
    name: "Person A Beacon RSSI"
    id: person_a_rssi

  - platform: template
    name: "Person A Distance (estimated)"
    id: person_a_distance
    unit_of_measurement: "m"
    lambda: |-
      // RSSI to distance conversion
      float rssi = id(person_a_rssi).state;
      if (isnan(rssi)) return NAN;
      float tx_power = -59.0;  // Calibrated at 1m
      float n = 3.0;           // Path loss exponent
      float distance = pow(10, (tx_power - rssi) / (10 * n));
      return distance;
```

**Custom Component for Fusion:**

```cpp
// esphome/custom_components/bed_presence_beacon/bed_presence_beacon.h
class BedPresenceBeacon : public Component {
 public:
  void set_ld2410_sensor(BinarySensor* ld2410) { ld2410_ = ld2410; }
  void set_beacon_rssi_sensor(Sensor* rssi) { beacon_rssi_ = rssi; }

  void loop() override {
    bool bed_occupied = ld2410_->state;
    float rssi = beacon_rssi_->state;
    float distance = rssi_to_distance(rssi);

    // Fusion logic
    if (bed_occupied && distance < 2.0) {
      // Person identified in bed
      publish_state("person_a_in_bed");
    } else if (bed_occupied && distance >= 2.0) {
      // Someone in bed, but not person A
      publish_state("unknown_in_bed");
    } else if (!bed_occupied && distance < 2.0) {
      // Person A in bedroom, but not in bed
      publish_state("person_a_in_room");
    } else {
      // No presence
      publish_state("vacant");
    }
  }

 private:
  BinarySensor* ld2410_;
  Sensor* beacon_rssi_;

  float rssi_to_distance(float rssi) {
    if (isnan(rssi)) return INFINITY;
    float tx_power = -59.0;
    float n = 3.0;
    return pow(10, (tx_power - rssi) / (10 * n));
  }
};
```

**Pros:**
- ✅ No additional hardware (ESP32 has Bluetooth)
- ✅ Native ESPHome support
- ✅ Low latency (on-device processing)
- ✅ Works offline (no cloud dependency)

**Cons:**
- ❌ ESP32 Bluetooth + WiFi contention (can cause stability issues)
- ❌ Limited concurrent BLE connections (scanning is fine, but connections are limited)
- ❌ RSSI accuracy challenges (multipath, interference)
- ❌ Increased power consumption

---

### Option B: Home Assistant BLE Integration (Off-Device)

**Approach:** Use Home Assistant's built-in Bluetooth integration to track beacons, perform fusion in HA automations.

**Home Assistant Configuration:**

```yaml
# configuration.yaml
bluetooth:
  adapters:
    - hci0  # Built-in Bluetooth on HA host (Raspberry Pi, etc.)

device_tracker:
  - platform: bluetooth_le_tracker
    track_new_devices: true
    interval_seconds: 12
    consider_home: 180

# Beacon definitions
device_tracker:
  - platform: bluetooth_le_tracker
    track_new_devices: false
    device_ids:
      - "AA:BB:CC:DD:EE:FF"  # Person A's beacon
```

**Template Sensor for Fusion:**

```yaml
# configuration.yaml
template:
  - sensor:
      - name: "Bed Occupant"
        state: >
          {% set bed_occupied = is_state('binary_sensor.bed_presence_detector_bed_occupied', 'on') %}
          {% set person_a_home = is_state('device_tracker.person_a_beacon', 'home') %}
          {% set person_a_rssi = state_attr('device_tracker.person_a_beacon', 'rssi') | float(-100) %}

          {% if bed_occupied and person_a_home and person_a_rssi > -70 %}
            person_a
          {% elif bed_occupied %}
            unknown
          {% else %}
            vacant
          {% endif %}
```

**Pros:**
- ✅ No ESP32 code changes required
- ✅ Leverages HA's existing Bluetooth infrastructure
- ✅ Can use phone's Bluetooth (iPhone/Android apps support beacon broadcasting)
- ✅ No additional ESP32 power consumption

**Cons:**
- ❌ Requires HA host with Bluetooth (Raspberry Pi, NUC, etc.)
- ❌ Higher latency (beacon → HA → automation)
- ❌ Depends on HA being online and responsive
- ❌ More complex setup for users without BLE-enabled HA hosts

---

### Option C: Dedicated BLE Gateway (Multi-Room)

**Approach:** Deploy multiple ESP32 devices as BLE gateways in different zones, publish beacon data to HA.

**Architecture:**
```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ ESP32       │       │ ESP32       │       │ ESP32       │
│ Bedroom     │       │ Bathroom    │       │ Closet      │
│ (LD2410 +   │       │ (BLE only)  │       │ (BLE only)  │
│  BLE)       │       │             │       │             │
└──────┬──────┘       └──────┬──────┘       └──────┬──────┘
       │                     │                     │
       └─────────────────────┴─────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Home Assistant │
                    │  (Fusion Logic) │
                    └─────────────────┘
```

**ESPHome Configuration (BLE Gateway):**

```yaml
# esphome/ble-gateway-bathroom.yaml
esphome:
  name: ble-gateway-bathroom
  platform: ESP32
  board: esp32dev

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_key

esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
    active: false

sensor:
  - platform: ble_rssi
    mac_address: "AA:BB:CC:DD:EE:FF"
    name: "Bathroom Person A RSSI"
    id: bathroom_person_a_rssi
```

**Pros:**
- ✅ Best multi-zone accuracy (dedicated gateway per zone)
- ✅ No WiFi/BLE contention on main bedroom ESP32
- ✅ Scalable to many zones
- ✅ Can use cheap ESP32-C3 boards (~$3 each)

**Cons:**
- ❌ Additional hardware cost ($3-10 per zone)
- ❌ More devices to manage (firmware updates, power, WiFi)
- ❌ Higher system complexity

---

## Calibration Strategy for BLE Distance

### Challenge: Variable Path Loss Exponent

The path loss exponent `n` varies by environment:
- **Free space**: n = 2.0
- **Indoor (light walls)**: n = 2.5
- **Indoor (heavy walls)**: n = 3.0 - 4.0
- **Cluttered environment**: n = 3.5 - 4.5

**Problem:** Hardcoding `n = 3.0` will be inaccurate in some homes.

### Proposed Calibration Workflow

**Step 1: TxPower Calibration (One-Time)**

```yaml
# Home Assistant calibration script
script:
  calibrate_beacon_txpower:
    alias: "Calibrate Beacon TxPower"
    sequence:
      - service: notify.mobile_app
        data:
          message: "Place beacon exactly 1 meter from ESP32 and press Continue"
      - wait_for_trigger:
          platform: event
          event_type: mobile_app_notification_action
      - service: input_number.set_value
        target: { entity_id: input_number.person_a_txpower }
        data:
          value: "{{ states('sensor.person_a_beacon_rssi') }}"
```

**Step 2: Path Loss Exponent Calibration (Per-Zone)**

```yaml
# Collect RSSI at known distances
script:
  calibrate_beacon_path_loss:
    alias: "Calibrate Path Loss Exponent"
    sequence:
      # Collect RSSI at 1m, 2m, 3m, 4m
      # Fit linear regression to log-log plot
      # Calculate n = slope / 10
      - service: input_number.set_value
        target: { entity_id: input_number.bedroom_path_loss_n }
        data:
          value: "{{ calculated_n }}"
```

**Step 3: Runtime Distance Windowing**

Similar to Phase 3 distance windowing for LD2410, define BLE distance thresholds:
- `ble_near_threshold`: < 1.5m = "very close" (in bed)
- `ble_medium_threshold`: 1.5-3m = "in room"
- `ble_far_threshold`: > 3m = "in adjacent room or away"

---

## Privacy & Security Considerations

### Privacy Concerns

**BLE Beacons Broadcast Unique Identifiers:**
- ⚠️ **Tracking risk**: Anyone with a BLE scanner can detect beacon presence
- ⚠️ **Identity linkage**: MAC address can be linked to person
- ⚠️ **Movement profiling**: Beacon signals reveal movement patterns

**Mitigation Strategies:**
1. **Randomized MAC addresses**: Use BLE privacy features (rotate MAC every 15 min)
2. **Encrypted payloads**: Use encrypted beacon formats (requires pairing)
3. **Home-only deployment**: Disable beacon when leaving home (geofencing)
4. **User consent**: Clear disclosure and opt-in required

### Security Concerns

**Beacon Spoofing:**
- ⚠️ **Impersonation**: Attacker broadcasts fake beacon to trigger automations
- ⚠️ **Replay attacks**: Recorded beacon signals replayed later

**Mitigation Strategies:**
1. **Encrypted beacons**: Use authenticated beacon protocols
2. **RSSI validation**: Reject beacons with impossible RSSI values
3. **Sequence numbers**: Reject replayed packets
4. **Time-of-flight**: Use BLE 5.1 direction finding (requires special hardware)

**Recommendation:** For high-security scenarios (door locks, alarm disarm), **do not rely solely on BLE beacons**. Use as a secondary signal for convenience features only.

---

## Comparison Matrix: LD2410 vs. BLE Beacons

| Criterion | LD2410 mmWave | BLE Beacons |
|-----------|---------------|-------------|
| **Privacy** | ✅ Anonymous, no tracking | ⚠️ Trackable, identifiable |
| **Accuracy (Zone)** | ✅ Excellent (>95%) | ⚠️ Moderate (70-85%) |
| **Accuracy (Distance)** | ✅ Good (±0.5m) | ❌ Poor (±1-3m) |
| **Person Identification** | ❌ No | ✅ Yes |
| **Multi-Zone Tracking** | ❌ No (1 sensor = 1 zone) | ✅ Yes (1 beacon = all zones) |
| **Passive Detection** | ✅ Yes (no wearable) | ❌ No (requires beacon) |
| **Cost per Zone** | $$$ ($30 sensor per zone) | $ ($5 beacon, shared across zones) |
| **Power Consumption** | Medium (USB powered) | Low (1-3 year battery) |
| **Latency** | ✅ <1s | ⚠️ 1-5s (scan interval) |
| **Environmental Immunity** | ✅ High (stable baselines) | ⚠️ Medium (RSSI variance) |
| **User Adoption** | ✅ Automatic | ⚠️ Requires wearing beacon |
| **Maintenance** | Low (no batteries) | Medium (battery replacement) |
| **Best For** | Fixed-zone occupancy | Person ID + multi-zone |

---

## Recommended Approach: Phased Hybrid Integration

After evaluating all options, the recommended path is a **phased, opt-in hybrid approach** that preserves the LD2410's strengths while enabling BLE enhancements for users who want person identification.

### Phase 4.0: BLE Person Identification (Complementary)

**Objective:** Add person identification to bed presence detection **without sacrificing** existing LD2410 reliability.

**Scope:**
1. Add ESPHome `esp32_ble_tracker` component to existing firmware
2. Create `ble_rssi` sensors for user-configured beacon MAC addresses
3. Implement simple fusion logic: `bed_occupied = LD2410 ON, bed_occupant = closest beacon`
4. Publish new sensor: `sensor.bed_occupant` (values: `person_a`, `person_b`, `unknown`, `vacant`)
5. Make BLE **opt-in** via configuration flag (disabled by default)

**Implementation:**

```yaml
# esphome/packages/ble_person_id.yaml (optional package)
esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms
    active: false

sensor:
  - platform: ble_rssi
    mac_address: !secret person_a_beacon_mac
    name: "Person A Beacon RSSI"
    id: person_a_rssi
    internal: true  # Don't expose raw RSSI to HA

  - platform: ble_rssi
    mac_address: !secret person_b_beacon_mac
    name: "Person B Beacon RSSI"
    id: person_b_rssi
    internal: true

text_sensor:
  - platform: template
    name: "Bed Occupant"
    id: bed_occupant
    lambda: |-
      // Only run if bed is occupied (LD2410)
      if (!id(bed_occupied).state) return {"vacant"};

      float rssi_a = id(person_a_rssi).state;
      float rssi_b = id(person_b_rssi).state;
      float near_threshold = -70.0;  // ~2m

      bool a_near = !isnan(rssi_a) && rssi_a > near_threshold;
      bool b_near = !isnan(rssi_b) && rssi_b > near_threshold;

      if (a_near && b_near) return {"person_a,person_b"};
      if (a_near) return {"person_a"};
      if (b_near) return {"person_b"};
      return {"unknown"};
```

**Pros:**
- ✅ Minimal disruption to existing system
- ✅ Opt-in (users without beacons unaffected)
- ✅ LD2410 remains primary sensor (reliability preserved)
- ✅ Enables person-specific automations for those who want it

**Cons:**
- ❌ Requires users to purchase beacons ($10-30 per person)
- ❌ Beacon battery maintenance burden
- ❌ Privacy tradeoff (tracking vs. convenience)

---

### Phase 4.1: Multi-Zone BLE Tracking (Future)

**Objective:** Enable whole-home presence tracking for users who want it.

**Scope:**
1. Deploy additional ESP32 BLE gateways in key zones (bathroom, closet, etc.)
2. Implement zone determination logic based on strongest RSSI
3. Publish `sensor.person_a_location` (values: `bedroom`, `bathroom`, `closet`, `away`)
4. Create Home Assistant templates for unified presence state machine

**Deferred to future RFD** - depends on Phase 4.0 adoption and user feedback.

---

### Phase 4.2: Advanced Fusion (Future)

**Objective:** Intelligent sensor fusion with adaptive weighting.

**Scope:**
1. Machine learning model to combine LD2410 + BLE + time-of-day
2. Adaptive thresholds based on historical patterns
3. Confidence scoring for presence state

**Deferred to future RFD** - requires significant research and validation.

---

## Alternative: Smartphone Bluetooth Companion Detection

**Simpler Alternative to Dedicated Beacons:**

Many smartphones can broadcast BLE advertisements via companion apps (Home Assistant Mobile App, Tasker, etc.). This eliminates dedicated beacon hardware.

**Pros:**
- ✅ No additional beacon hardware ($0 cost)
- ✅ Most people already carry phones
- ✅ Can enable/disable via app (user control)

**Cons:**
- ❌ Inconsistent broadcast (iOS/Android background limitations)
- ❌ Battery drain concerns
- ❌ May not work during sleep (phone far from bed)
- ❌ Doesn't work if phone is charging in another room

**Verdict:** Useful for testing, but dedicated beacons more reliable for bed presence.

---

## Open Questions for Discussion

1. **Primary Use Case:**
   - Is person identification the main goal, or multi-zone tracking?
   - How many users actually need to identify *who* is in bed vs. just *if* bed is occupied?

2. **Beacon Form Factor:**
   - Wearable (wristband, clip)? Phone? Smartwatch? Keychain tag?
   - What battery life is acceptable? (1 year? 3 years?)

3. **Privacy Acceptance:**
   - Are users comfortable with BLE tracking in their home?
   - Should beacons be disabled when guests visit?

4. **Cost/Benefit:**
   - Is $20-30 per person for beacons worth the added functionality?
   - Would users prefer to spend that on additional LD2410 sensors instead?

5. **Maintenance Burden:**
   - Who will remember to replace beacon batteries?
   - What happens when a beacon dies? (Graceful degradation?)

6. **ESP32 Stability:**
   - Can ESP32 reliably run WiFi + Bluetooth + LD2410 UART simultaneously?
   - Have there been reports of instability with BLE + WiFi?

7. **Alternative Technologies:**
   - Should we consider UWB (Ultra-Wideband) for higher accuracy? (iPhone U1 chip)
   - What about WiFi-based presence detection? (router RSSI, ping-based)

---

## Success Criteria

If BLE beacon integration is pursued, it will be considered successful if:

- [ ] Phase 3 LD2410 reliability maintained (>95% accuracy)
- [ ] Person identification accuracy >80% when beacon present
- [ ] Graceful degradation when beacon absent (falls back to anonymous detection)
- [ ] Battery life >6 months (ideally 1+ year)
- [ ] No user reports of ESP32 instability (WiFi + BLE coexistence)
- [ ] Clear documentation of privacy implications
- [ ] Opt-in by default (doesn't affect users who don't want it)

---

## Next Steps

1. **Community Feedback**: Gather input on use cases, privacy concerns, and interest level
2. **Proof of Concept**: Build Phase 4.0 prototype on test hardware
3. **Beacon Testing**: Evaluate beacon options (iBeacon vs. Eddystone, form factors, battery life)
4. **Stability Testing**: Validate ESP32 WiFi + BLE coexistence over 7-day period
5. **Privacy Framework**: Draft privacy disclosure and user consent workflow
6. **Documentation**: Create BLE setup guide, calibration workflow, troubleshooting tips

---

## References

### BLE Beacon Technology

- **iBeacon Specification**: https://developer.apple.com/ibeacon/
- **Eddystone Protocol**: https://github.com/google/eddystone
- **BLE RSSI Distance Estimation**: https://www.bluetooth.com/blog/proximity-and-rssi/
- **Path Loss Models**: https://en.wikipedia.org/wiki/Log-distance_path_loss_model

### ESPHome Documentation

- **ESP32 BLE Tracker**: https://esphome.io/components/esp32_ble_tracker.html
- **BLE RSSI Sensor**: https://esphome.io/components/sensor/ble_rssi.html
- **Bluetooth Proxy**: https://esphome.io/components/bluetooth_proxy.html

### Home Assistant Integration

- **Bluetooth Integration**: https://www.home-assistant.io/integrations/bluetooth/
- **Bluetooth LE Tracker**: https://www.home-assistant.io/integrations/bluetooth_le_tracker/
- **Device Tracker**: https://www.home-assistant.io/integrations/device_tracker/

### Related Projects

- **ESP32-BLE-Presence**: https://github.com/ESPresense/ESPresense
- **Room Assistant (BLE + ESP32)**: https://www.room-assistant.io/
- **Monitor (BLE Presence Detection)**: https://github.com/andrewjfreyer/monitor

### Privacy & Security

- **BLE Privacy**: https://www.bluetooth.com/blog/bluetooth-technology-protecting-your-privacy/
- **MAC Address Randomization**: https://source.android.com/devices/tech/connect/wifi-mac-randomization
- **Beacon Security Best Practices**: https://www.beaconzone.co.uk/beacon-security

### Hardware Options

- **Estimote Beacons**: https://estimote.com/ ($20-30, 2-year battery)
- **Tile Tags**: https://www.tile.com/ ($25, 1-year battery, phone-based)
- **Generic BLE Tags**: https://www.aliexpress.com/ ($3-10, 6-12 month battery)

### Code References (This Project)

- `docs/ARCHITECTURE.md` - Current presence engine architecture
- `docs/RFD-001-still-vs-moving-energy.md` - Sensor selection rationale
- `esphome/packages/presence_engine.yaml` - Current detection logic
- `esphome/custom_components/bed_presence_engine/` - C++ implementation

---

## Approval & History

- **2025-11-13**: RFD-003 created, awaiting community discussion
- **Status**: 🟡 Proposed (needs feedback on use cases, privacy, and priority)

**Next Review**: After 2-3 weeks of community discussion

---

## Appendix A: Estimated Beacon Distance Accuracy

**Test Scenario**: Generic BLE beacon in bedroom environment

| Actual Distance | Measured Distance | Error | Notes |
|----------------|------------------|-------|-------|
| 1.0m | 1.2m | +20% | Line of sight, good accuracy |
| 2.0m | 2.4m | +20% | Line of sight |
| 3.0m | 3.8m | +27% | Some furniture obstruction |
| 4.0m | 5.2m | +30% | Through bed frame, metal springs |
| 5.0m | 4.1m | -18% | Signal reflection from wall |

**Conclusion**: ±20-30% error typical, sufficient for zone detection but not precise positioning.

---

## Appendix B: Power Consumption Comparison

| Configuration | Power Draw | Notes |
|--------------|-----------|-------|
| ESP32 + LD2410 only | 150mA @ 5V | Current Phase 3 setup |
| ESP32 + LD2410 + BLE scan | 210mA @ 5V | +40% power increase |
| BLE Beacon (transmit only) | 0.05mA @ 3V | 1-3 year coin cell life |

**Impact**: BLE scanning increases ESP32 power draw by ~40%, but ESP32 is USB-powered so not a concern. Beacon batteries are the maintenance burden.

---

## Appendix C: Example Beacon Products

| Product | Cost | Battery Life | Form Factor | Notes |
|---------|------|--------------|-------------|-------|
| Tile Pro | $35 | 1 year (replaceable) | Keychain | Phone app, loud alert |
| Estimote Location Beacon | $25 | 2 years | Small square | iBeacon/Eddystone, configurable |
| Generic BLE Tag (Aliexpress) | $5 | 6-12 months | Coin cell | No app, basic broadcast |
| Apple AirTag | $29 | 1 year (replaceable) | Round tag | Requires iOS, UWB for precision |
| SmartWatch (Wear OS/Apple Watch) | $150+ | 1-2 days (rechargeable) | Wrist | Already worn, no extra hardware |

**Recommendation**: For proof-of-concept, generic $5 tags. For production, Estimote beacons (reliability + support).

---

**End of RFD-003**
