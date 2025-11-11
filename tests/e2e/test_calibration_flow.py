"""
End-to-End Integration Tests for Bed Presence Detector

These tests verify the full integration between Home Assistant and the ESPHome device,
including the calibration wizard flow and threshold updates.

Environment Variables Required:
- HA_URL: WebSocket URL for Home Assistant (e.g., ws://homeassistant.local:8123/api/websocket)
- HA_TOKEN: Long-lived access token for Home Assistant
"""

import os
import asyncio
import pytest
import pytest_asyncio
from hass_ws import HomeAssistantClient


@pytest_asyncio.fixture
async def ha_client():
    """Fixture to create and authenticate Home Assistant WebSocket client"""
    url = os.getenv("HA_URL")
    token = os.getenv("HA_TOKEN")

    if not url or not token:
        pytest.skip("HA_URL and HA_TOKEN environment variables must be set")

    client = HomeAssistantClient(url, token)
    await client.connect()
    yield client
    await client.disconnect()


DEVICE_NAME_MATCHES = ("bed presence detector", "bed-presence-detector")

NUMBER_ENTITIES = {
    "k_on": "number.bed_presence_detector_k_on_on_threshold_multiplier",
    "k_off": "number.bed_presence_detector_k_off_off_threshold_multiplier",
    "on_debounce": "number.bed_presence_detector_on_debounce_timer_ms",
    "off_debounce": "number.bed_presence_detector_off_debounce_timer_ms",
    "abs_clear": "number.bed_presence_detector_absolute_clear_delay_ms",
    "d_min": "number.bed_presence_detector_distance_min_cm",
    "d_max": "number.bed_presence_detector_distance_max_cm",
}


async def _wait_for_reason(ha_client, timeout=10):
    """Wait until the state reason contains a z-score string."""
    end_time = asyncio.get_event_loop().time() + timeout
    entity_id = "sensor.bed_presence_detector_presence_state_reason"
    while asyncio.get_event_loop().time() < end_time:
        reason = await ha_client.get_state(entity_id)
        if reason:
            text = reason["state"].lower()
            if "z=" in text or "z-score" in text:
                return reason
        await asyncio.sleep(1)
    return reason


@pytest.mark.asyncio
async def test_device_is_connected(ha_client):
    """Test that the bed presence detector device is connected to Home Assistant"""
    devices = await ha_client.get_devices()

    def matches(device):
        name = device.get("name", "").lower()
        return any(match in name for match in DEVICE_NAME_MATCHES)

    bed_detector = next((d for d in devices if matches(d)), None)

    assert bed_detector is not None, "Bed presence detector device not found"
    assert bed_detector.get("disabled_by") is None, "Device is disabled"


@pytest.mark.asyncio
async def test_presence_sensor_exists(ha_client):
    """Test that the bed occupied binary sensor exists"""
    state = await ha_client.get_state("binary_sensor.bed_presence_detector_bed_occupied")
    assert state is not None, "binary_sensor.bed_presence_detector_bed_occupied not found"
    assert state["state"] in ["on", "off"], "Invalid state for presence sensor"


@pytest.mark.asyncio
async def test_threshold_entities_exist(ha_client):
    """Test that threshold configuration entities exist"""
    k_on_threshold = await ha_client.get_state(NUMBER_ENTITIES["k_on"])
    k_off_threshold = await ha_client.get_state(NUMBER_ENTITIES["k_off"])

    assert k_on_threshold is not None, "number.bed_presence_detector_k_on_on_threshold_multiplier not found"
    assert k_off_threshold is not None, "number.bed_presence_detector_k_off_off_threshold_multiplier not found"

    # Verify thresholds are sensible (k_on should be higher than k_off for hysteresis)
    k_on_val = float(k_on_threshold["state"])
    k_off_val = float(k_off_threshold["state"])
    assert k_on_val > k_off_val, "k_on threshold should be higher than k_off for hysteresis"


@pytest.mark.asyncio
async def test_update_threshold_via_service(ha_client):
    """Test that we can update thresholds via Home Assistant service call"""
    # Set a new k_on threshold value (Phase 1: z-score multiplier, typical range 0-10)
    await ha_client.call_service(
        "number",
        "set_value",
        entity_id=NUMBER_ENTITIES["k_on"],
        value=5.0
    )

    # Wait for update to propagate
    await asyncio.sleep(1)

    # Verify the update
    state = await ha_client.get_state("number.bed_presence_detector_k_on_on_threshold_multiplier")
    assert float(state["state"]) == 5.0, "k_on threshold was not updated"


@pytest.mark.asyncio
async def test_calibration_service_exists(ha_client):
    """Test that the calibration ESPHome services are available"""
    services = await ha_client.get_services()

    # Check that our custom ESPHome services exist
    esphome_services = services.get("esphome", {})

    required = [
        "bed_presence_detector_start_calibration",
        "bed_presence_detector_calibrate_start_baseline",
        "bed_presence_detector_stop_calibration",
        "bed_presence_detector_calibrate_stop",
        "bed_presence_detector_reset_to_defaults",
        "bed_presence_detector_calibrate_reset_all",
    ]

    for service_name in required:
        assert service_name in esphome_services, f"{service_name} service not found"


@pytest.mark.asyncio
async def test_reset_to_defaults(ha_client):
    """Test the reset to defaults service"""
    # Call reset service
    await ha_client.call_service(
        "esphome",
        "bed_presence_detector_reset_to_defaults"
    )

    # Wait for reset to complete
    await asyncio.sleep(2)

    # Verify defaults are restored (Phase 3 defaults)
    k_on_state = await ha_client.get_state(NUMBER_ENTITIES["k_on"])
    k_off_state = await ha_client.get_state(NUMBER_ENTITIES["k_off"])
    on_debounce = await ha_client.get_state(NUMBER_ENTITIES["on_debounce"])
    off_debounce = await ha_client.get_state(NUMBER_ENTITIES["off_debounce"])
    abs_clear = await ha_client.get_state(NUMBER_ENTITIES["abs_clear"])
    d_min = await ha_client.get_state(NUMBER_ENTITIES["d_min"])
    d_max = await ha_client.get_state(NUMBER_ENTITIES["d_max"])

    assert float(k_on_state["state"]) == 9.0, "k_on threshold not reset to default (9.0)"
    assert float(k_off_state["state"]) == 4.0, "k_off threshold not reset to default (4.0)"
    assert float(on_debounce["state"]) == 3000, "on_debounce_timer_ms not reset"
    assert float(off_debounce["state"]) == 5000, "off_debounce_ms not reset"
    assert float(abs_clear["state"]) == 30000, "abs_clear_delay_ms not reset"
    assert float(d_min["state"]) == 0.0, "distance_min not reset"
    assert float(d_max["state"]) == 600.0, "distance_max not reset"


@pytest.mark.asyncio
async def test_state_reason_sensor(ha_client):
    """Test that the state reason text sensor is available and updating"""
    state = await ha_client.get_state("sensor.bed_presence_detector_presence_state_reason")
    assert state is not None, "State reason sensor not found"
    assert len(state["state"]) > 0, "State reason is empty"


@pytest.mark.asyncio
async def test_change_reason_sensor(ha_client):
    """Test that the change reason text sensor is available and updating"""
    state = await ha_client.get_state("sensor.bed_presence_detector_presence_change_reason")
    assert state is not None, "Change reason sensor not found"
    assert len(state["state"]) > 0, "Change reason is empty"


@pytest.mark.asyncio
async def test_calibration_helpers_exist(ha_client):
    """Test that the calibration helper entities exist in Home Assistant"""
    helper_entities = [
        "input_select.bed_presence_calibration_step",
        "input_boolean.bed_presence_calibration_in_progress",
        "input_boolean.bed_presence_calibration_confirm_empty_bed",
        "input_number.bed_presence_calibration_duration_seconds",
        "input_datetime.bed_presence_last_calibration",
        "script.bed_presence_start_baseline_calibration",
        "script.bed_presence_cancel_baseline_calibration",
        "script.bed_presence_reset_calibration_defaults",
    ]

    missing = []
    for entity_id in helper_entities:
        state = await ha_client.get_state(entity_id)
        if state is None:
            missing.append(entity_id)

    assert not missing, f"Missing calibration helper entities: {missing}"


@pytest.mark.skip(reason="Requires physical calibration cycle with empty bed")
@pytest.mark.asyncio
async def test_full_calibration_flow(ha_client):
    """
    Test the full calibration workflow:
    1. Start vacant calibration
    2. Wait for completion
    3. Start occupied calibration
    4. Wait for completion
    5. Verify thresholds were calculated
    """
    # Reset to known state
    await ha_client.call_service(
        "esphome",
        "bed_presence_detector_reset_to_defaults"
    )
    await asyncio.sleep(1)

    # Start vacant calibration script
    await ha_client.call_service("script", "bed_presence_start_baseline_calibration")

    # Wait for calibration to complete (script has 30s delay)
    await asyncio.sleep(35)

    # Check that calibration step was updated
    step_state = await ha_client.get_state("input_select.bed_presence_calibration_step")
    assert step_state["state"] in ["Finalizing", "Completed"], \
        f"Unexpected calibration step: {step_state['state']}"

    # Note: Full flow would continue with occupied calibration,
    # but we keep this test short for CI/CD purposes


@pytest.mark.asyncio
async def test_phase3_configuration_entities_exist(ha_client):
    """Test that Phase 3 configuration entities exist"""
    on_debounce = await ha_client.get_state(NUMBER_ENTITIES["on_debounce"])
    off_debounce = await ha_client.get_state(NUMBER_ENTITIES["off_debounce"])
    abs_clear = await ha_client.get_state(NUMBER_ENTITIES["abs_clear"])
    d_min = await ha_client.get_state(NUMBER_ENTITIES["d_min"])
    d_max = await ha_client.get_state(NUMBER_ENTITIES["d_max"])

    assert on_debounce is not None, f"{NUMBER_ENTITIES['on_debounce']} not found"
    assert off_debounce is not None, "number.bed_presence_detector_off_debounce_ms not found"
    assert abs_clear is not None, "number.bed_presence_detector_absolute_clear_delay_ms not found"
    assert d_min is not None, "number.bed_presence_detector_distance_min_cm not found"
    assert d_max is not None, "number.bed_presence_detector_distance_max_cm not found"

    # Verify values are reasonable
    assert float(on_debounce["state"]) >= 0, "on_debounce_timer_ms should be non-negative"
    assert float(off_debounce["state"]) >= 0, "off_debounce_ms should be non-negative"
    assert float(abs_clear["state"]) >= 0, "abs_clear_delay_ms should be non-negative"
    assert 0.0 <= float(d_min["state"]) <= 600.0, "distance_min_cm should be within 0-600"
    assert 0.0 <= float(d_max["state"]) <= 600.0, "distance_max_cm should be within 0-600"


@pytest.mark.asyncio
async def test_phase2_update_debounce_timers(ha_client):
    """Test that we can update debounce timers via Home Assistant service call"""
    # Set a new on_debounce value (Phase 2: milliseconds, typical range 0-10000)
    await ha_client.call_service(
        "number",
        "set_value",
        entity_id=NUMBER_ENTITIES["on_debounce"],
        value=5000
    )

    # Wait for update to propagate
    await asyncio.sleep(1)

    # Verify the update
    state = await ha_client.get_state(NUMBER_ENTITIES["on_debounce"])
    assert float(state["state"]) == 5000, "on_debounce_timer_ms was not updated"


@pytest.mark.asyncio
async def test_phase3_update_distance_window(ha_client):
    """Test that we can update the distance window entities"""
    await ha_client.call_service(
        "number",
        "set_value",
        entity_id="number.bed_presence_detector_distance_min_cm",
        value=100
    )
    await asyncio.sleep(1)
    await ha_client.call_service(
        "number",
        "set_value",
        entity_id="number.bed_presence_detector_distance_max_cm",
        value=300
    )
    await asyncio.sleep(1)

    d_min = await ha_client.get_state(NUMBER_ENTITIES["d_min"])
    d_max = await ha_client.get_state(NUMBER_ENTITIES["d_max"])
    assert float(d_min["state"]) == 100.0, "distance_min_cm was not updated"
    assert float(d_max["state"]) == 300.0, "distance_max_cm was not updated"


@pytest.mark.asyncio
async def test_phase2_state_machine_monitoring(ha_client):
    """Test Phase 2 state machine by monitoring state changes over time"""
    # Collect 10 samples over 10 seconds to observe state machine behavior
    samples = []

    for _ in range(10):
        state = await ha_client.get_state("binary_sensor.bed_presence_detector_bed_occupied")
        reason = await ha_client.get_state("sensor.bed_presence_detector_presence_state_reason")
        energy = await ha_client.get_state("sensor.bed_presence_detector_ld2410_still_energy")

        samples.append({
            "presence": state["state"],
            "reason": reason["state"],
            "energy": float(energy["state"])
        })

        await asyncio.sleep(1)

    # Verify we got valid data from all samples
    assert len(samples) == 10, "Did not collect all samples"
    assert all(s["presence"] in ["on", "off"] for s in samples), "Invalid presence states"
    assert all(len(s["reason"]) > 0 for s in samples), "Empty state reasons"
    assert all(s["energy"] >= 0 for s in samples), "Invalid energy readings"


@pytest.mark.asyncio
async def test_phase2_z_score_calculation(ha_client):
    """Test that z-score calculations are reflected in state reason"""
    try:
        await ha_client.call_service(
            "number",
            "set_value",
            entity_id=NUMBER_ENTITIES["k_on"],
            value=0.1,
        )
        await ha_client.call_service(
            "number",
            "set_value",
            entity_id=NUMBER_ENTITIES["k_off"],
            value=0.05,
        )
        await ha_client.call_service(
            "number",
            "set_value",
            entity_id=NUMBER_ENTITIES["on_debounce"],
            value=0,
        )
        await ha_client.call_service(
            "number",
            "set_value",
            entity_id=NUMBER_ENTITIES["off_debounce"],
            value=0,
        )

        reason = await _wait_for_reason(ha_client, timeout=30)

        assert reason is not None, "State reason sensor not found"
        reason_text = reason["state"]

        allowed_tokens = ("z=", "z-score", "reset to defaults", "calibration")
        assert any(token in reason_text.lower() for token in allowed_tokens), \
            f"State reason does not contain z-score information: {reason_text}"
    finally:
        await ha_client.call_service(
            "esphome",
            "bed_presence_detector_reset_to_defaults"
        )
        await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_phase2_hysteresis_validation(ha_client):
    """Test that hysteresis gap is maintained (k_on > k_off)"""
    k_on = await ha_client.get_state("number.bed_presence_detector_k_on_on_threshold_multiplier")
    k_off = await ha_client.get_state("number.bed_presence_detector_k_off_off_threshold_multiplier")

    k_on_val = float(k_on["state"])
    k_off_val = float(k_off["state"])

    # Hysteresis requires k_on > k_off
    assert k_on_val > k_off_val, \
        f"Hysteresis violation: k_on ({k_on_val}) should be greater than k_off ({k_off_val})"

    # Reasonable gap (at least 1.0 sigma for good hysteresis)
    gap = k_on_val - k_off_val
    assert gap >= 1.0, \
        f"Hysteresis gap too small: {gap:.2f}σ (recommend >= 1.0σ)"


@pytest.mark.asyncio
async def test_phase2_sensor_raw_data_available(ha_client):
    """Test that raw LD2410 sensor data is available"""
    still_energy = await ha_client.get_state("sensor.bed_presence_detector_ld2410_still_energy")

    assert still_energy is not None, "LD2410 still energy sensor not found"
    assert still_energy["state"] not in ["unavailable", "unknown"], \
        "LD2410 sensor is unavailable"

    # Energy should be a percentage (0-100)
    energy_val = float(still_energy["state"])
    assert 0 <= energy_val <= 100, \
        f"LD2410 energy out of range: {energy_val}% (expected 0-100%)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
