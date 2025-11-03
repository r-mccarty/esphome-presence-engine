# Phase 1 Hardware Setup Checklist

This document guides you through setting up and testing the Phase 1 firmware with actual hardware.

## Prerequisites

- ✅ M5Stack Basic v2.7
- ⏳ LD2410C mmWave radar sensor (arriving later today)
- ✅ ESPHome firmware compiled successfully
- ✅ Home Assistant running and accessible

## Step 1: Verify Current ESPHome Configuration

Before connecting the LD2410 sensor, verify your existing M5Stack firmware:

1. **Check M5Stack Connection**
   - Go to Home Assistant → Settings → Devices & Services → ESPHome
   - Verify `bed-presence-detector` is online
   - Note: It won't have presence detection yet (waiting for LD2410)

2. **Update secrets.yaml**
   - File: `esphome/secrets.yaml`
   - Replace placeholder values:
     - `wifi_ssid`: Your actual Wi-Fi network name
     - `wifi_password`: Your Wi-Fi password
     - `ota_password`: Choose a secure OTA update password
   - Keep the `api_encryption_key` as-is (or generate a new one)

## Step 2: Connect LD2410 to M5Stack

**Wiring configuration** (per `esphome/packages/hardware_m5stack_ld2410.yaml`):

| LD2410 Pin | M5Stack Pin | Purpose           |
|------------|-------------|-------------------|
| TX         | GPIO16 (RX) | UART receive      |
| RX         | GPIO17 (TX) | UART transmit     |
| VCC        | 5V          | Power supply      |
| GND        | GND         | Ground            |

**Important notes:**
- ⚠️ TX on LD2410 connects to RX on M5Stack (cross-over)
- ⚠️ RX on LD2410 connects to TX on M5Stack (cross-over)
- The LD2410 operates at 256000 baud (configured in YAML)

## Step 3: Collect Baseline Data

Before updating hardcoded μ and σ values, you need to collect baseline energy readings from an **empty bed**.

### 3A. Flash Current Firmware (Temporary)

```bash
cd esphome
esphome run bed-presence-detector.yaml
```

Choose your M5Stack device and flash.

### 3B. Observe Energy Values

1. Go to Home Assistant → Developer Tools → States
2. Find these entities:
   - `sensor.ld2410_moving_energy`
   - `sensor.ld2410_still_energy`
3. **Leave the bed completely empty** for 60 seconds
4. **Record the values** you observe:
   - Watch for typical values (e.g., mostly around 40-60)
   - Note the range of variation (e.g., occasionally spikes to 80)

### 3C. Calculate Baseline Statistics

You need to estimate **μ** (mean) and **σ** (standard deviation):

**Moving Energy:**
- μ_move = Typical value when empty (e.g., 50)
- σ_move = How much it varies (e.g., 15)
  - If values range from 40-60, σ ≈ 10
  - If values range from 30-70, σ ≈ 20

**Still/Static Energy:**
- μ_stat = Typical value when empty (e.g., 80)
- σ_stat = How much it varies (e.g., 10)

**Example observations:**
```
Moving energy: Usually 45-55, occasionally spikes to 65
Still energy: Usually 75-85, very stable

Estimates:
μ_move = 50
σ_move = 10
μ_stat = 80
σ_stat = 5
```

## Step 4: Update Hardcoded Values

Edit `esphome/custom_components/bed_presence_engine/bed_presence.h`:

```cpp
// Line 43-46: Replace with your observed values
float mu_move_{50.0f};    // Your μ_move value
float sigma_move_{10.0f}; // Your σ_move value
float mu_stat_{80.0f};    // Your μ_stat value
float sigma_stat_{5.0f};  // Your σ_stat value
```

**Note:** Phase 1 currently uses `still_energy` (static), but the code is ready for both moving and static.

## Step 5: Recompile and Flash Phase 1 Firmware

```bash
cd esphome
esphome compile bed-presence-detector.yaml
esphome run bed-presence-detector.yaml
```

Wait for the device to reboot and reconnect to Home Assistant.

## Step 6: Verify Phase 1 Operation

### 6A. Check Entities in Home Assistant

You should now see:

**Binary Sensor:**
- `binary_sensor.bed_occupied` - Main presence detection (OFF initially)

**Number Inputs (tunable via UI):**
- `number.k_on_on_threshold_multiplier` - Default: 4.0
- `number.k_off_off_threshold_multiplier` - Default: 2.0

**Text Sensor:**
- `text_sensor.presence_state_reason` - Shows why state last changed

**Raw Sensors (for debugging):**
- `sensor.ld2410_moving_energy`
- `sensor.ld2410_still_energy`
- `sensor.ld2410_moving_distance`
- etc.

### 6B. Test Detection

**Test 1: Immediate ON (no debouncing)**
1. With empty bed, note that `bed_occupied` is OFF
2. Wave your hand vigorously in front of the sensor
3. **Expected:** `bed_occupied` turns ON **immediately**
4. Check `presence_state_reason` - should show: `ON: z=X.XX > k_on=4.00`

**Test 2: Immediate OFF (twitchy behavior)**
1. While `bed_occupied` is ON
2. Remain perfectly still or move away
3. **Expected:** `bed_occupied` turns OFF **immediately** (within 1-2 seconds)
4. Check `presence_state_reason` - should show: `OFF: z=X.XX < k_off=2.00`

**Test 3: Hysteresis**
1. Turn ON the sensor
2. Move slowly and gently (moderate energy)
3. **Expected:** Sensor should stay ON even if energy drops between k_off and k_on
4. Only turns OFF when energy drops significantly below baseline

### 6C. Validate "Twitchy" Behavior

**This is expected for Phase 1!**

- Rapid ON/OFF transitions
- Responds to small movements
- No smoothing or filtering
- Sensitive to fan noise, AC vents, etc.

This validates the core z-score concept. Phase 2 will add temporal filtering.

## Step 7: Tune Thresholds (Optional)

If the sensor is too sensitive or not sensitive enough:

### Make it LESS sensitive (harder to trigger):
- Increase `k_on` from 4.0 → 5.0 or 6.0
- This requires a stronger signal (higher z-score) to turn ON

### Make it MORE sensitive (easier to trigger):
- Decrease `k_on` from 4.0 → 3.0 or 2.5
- This triggers ON with weaker signals

### Adjust hysteresis (prevent flapping):
- Keep `k_on` > `k_off` by at least 1.0-2.0
- Larger gap = more stable (but less responsive)
- Smaller gap = more responsive (but may flap)

**Adjust via Home Assistant:**
- Go to Settings → Devices & Services → ESPHome → bed-presence-detector
- Find the `number` entities and adjust sliders
- Changes take effect immediately (no reboot needed)

## Step 8: Monitor Logs (Debugging)

If something isn't working:

```bash
cd esphome
esphome logs bed-presence-detector.yaml
```

Look for:
- `[bed_presence_engine] Setting up Bed Presence Engine (Phase 1)...`
- `[bed_presence_engine] Baseline (moving): μ=X.XX, σ=X.XX`
- `[bed_presence_engine] Presence detected: ON: z=X.XX > k_on=X.XX`
- `[bed_presence_engine] Presence cleared: OFF: z=X.XX < k_off=X.XX`

## Troubleshooting

### Sensor always OFF
- LD2410 may not be wired correctly (check TX/RX crossover)
- Baseline values (μ, σ) may be incorrect - recollect data
- k_on threshold may be too high - try lowering to 3.0

### Sensor always ON
- Baseline μ may be too high
- k_off threshold may be too high
- Check for nearby fans, AC vents causing constant motion

### Sensor not appearing in HA
- Check Wi-Fi credentials in `secrets.yaml`
- Verify M5Stack is on same network as Home Assistant
- Check ESPHome logs for connection errors

### Energy values are 0 or not updating
- LD2410 not powered correctly
- UART wiring reversed or incorrect
- Baud rate mismatch (should be 256000)

## Phase 1 Success Criteria

✅ **Phase 1 is complete when:**
1. `bed_occupied` sensor appears in Home Assistant
2. Sensor turns ON immediately when waving hand
3. Sensor turns OFF immediately when still
4. State is "twitchy" (no debouncing, rapid changes)
5. `presence_state_reason` shows z-scores in logs
6. Can tune `k_on` and `k_off` from HA UI

## Next Steps

Once Phase 1 is validated:
- Document what k_on/k_off values work best for your bed
- Note any false positives (fan, AC, etc.)
- Prepare for **Phase 2**: Temporal filtering and state machine
  - Will add debounce timers
  - Will eliminate "twitchy" behavior
  - Will require configuration of on/off debounce delays

## Quick Reference

**Default Phase 1 Parameters:**
- μ_move = 100.0 (placeholder - UPDATE THIS)
- σ_move = 20.0 (placeholder - UPDATE THIS)
- k_on = 4.0 (4 standard deviations to turn ON)
- k_off = 2.0 (2 standard deviations to turn OFF)

**Phase 1 Logic:**
```
z_score = (energy - μ) / σ
if (not occupied and z_score > k_on): turn ON
if (occupied and z_score < k_off): turn OFF
```

**Key Files:**
- Firmware config: `esphome/bed-presence-detector.yaml`
- Hardware config: `esphome/packages/hardware_m5stack_ld2410.yaml`
- C++ engine: `esphome/custom_components/bed_presence_engine/bed_presence.cpp`
- Baseline values: `bed_presence.h` lines 43-46
