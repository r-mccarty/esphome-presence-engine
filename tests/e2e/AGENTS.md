# AGENTS.md – End-to-End Integration Tests

Guidance for agents working on the async pytest suite under `tests/e2e/`. These tests verify the deployed ESPHome device through the Home Assistant WebSocket API. **Always read `../../CLAUDE.md` first**, then consult:
- `docs/ARCHITECTURE.md` for entity structure and expected behavior
- `docs/DEVELOPMENT_WORKFLOW.md` for the **critical two-machine workflow**

## ⚠️ CRITICAL: Must Run on ubuntu-node

**These tests CANNOT run in Codespaces** due to network isolation from Home Assistant (192.168.0.148).

### Running the Suite (on ubuntu-node only)

```bash
# SSH to ubuntu-node
ssh user@ubuntu-node

# Navigate to test directory
cd ~/bed-presence-sensor/tests/e2e

# Install dependencies (first time only)
pip install -r requirements.txt

# Verify .env.local exists with HA credentials
cat ~/.env.local  # Should contain HA_URL and HA_TOKEN

# Run full test suite (Phase 3 tests auto-skipped)
pytest -v

# Run specific test categories
pytest -v -k "debounce"    # Debounce timer tests
pytest -v -k "threshold"   # Threshold configuration tests
pytest -v -k "calibration" # Calibration tests (currently skipped)
```

## Current Scope (Phase 2)
- ✅ **Device connectivity**: Verify ESPHome device is online and responsive
- ✅ **Binary sensor availability**: Check `binary_sensor.bed_presence_detector_bed_occupied` exists
- ✅ **Runtime threshold controls**: Test k_on/k_off number entities update correctly
- ✅ **Debounce timer controls**: Test on/off/absolute-clear debounce timers (Phase 2 addition)
- ✅ **State reason telemetry**: Verify `text_sensor` provides z-score diagnostics
- ✅ **ESPHome services**: Test service calls (reset_to_defaults, start/stop_calibration stubs)
- ⏸️ **Calibration helpers**: Skipped until Phase 3 implementation (services only log messages)

## Environment Requirements

### Home Assistant Setup
- **Version**: Home Assistant ≥ 2023.8
- **Access**: WebSocket API must be accessible from ubuntu-node
- **Device**: ESPHome device "bed-presence-detector" provisioned and online
- **Network**: ubuntu-node must be able to reach HA at 192.168.0.148

### Required Entity IDs (Phase 2 Firmware)

**Binary Sensor:**
- `binary_sensor.bed_presence_detector_bed_occupied` (debounced presence state)

**Configuration Controls:**
- `number.bed_presence_detector_k_on_on_threshold_multiplier` (default: 9.0)
- `number.bed_presence_detector_k_off_off_threshold_multiplier` (default: 4.0)
- `number.bed_presence_detector_on_debounce_timer_ms` (default: 3000)
- `number.bed_presence_detector_off_debounce_timer_ms` (default: 5000)
- `number.bed_presence_detector_absolute_clear_delay_ms` (default: 30000)

**Diagnostic Sensors:**
- `text_sensor.bed_presence_detector_presence_state_reason` (z-score + state machine info)
- `sensor.bed_presence_detector_ld2410_still_energy` (raw sensor data)

**ESPHome Services:**
- `esphome.bed_presence_detector_start_calibration` (Phase 3 stub, only logs)
- `esphome.bed_presence_detector_stop_calibration` (Phase 3 stub, only logs)
- `esphome.bed_presence_detector_reset_to_defaults` (functional)

### Credentials Configuration

**Location**: `~/.env.local` on ubuntu-node (NOT in repository)

**Required variables:**
```bash
HA_URL=ws://192.168.0.148:8123/api/websocket
HA_TOKEN=your_long_lived_access_token_here
```

**⚠️ CRITICAL**: Ubuntu-node is the source of truth for `.env.local`. Never copy FROM Codespaces TO ubuntu-node.

## Writing Tests

### Best Practices
- **Async patterns**: Use `await asyncio.sleep()` sparingly; prefer polling loops with timeouts for state changes
- **Fixture defaults**: Always mirror firmware defaults in assertions:
  - k_on = 9.0, k_off = 4.0
  - on_debounce = 3000ms, off_debounce = 5000ms, absolute_clear = 30000ms
  - Baseline: μ = 6.7%, σ = 3.5%
- **Phase markers**: Tag Phase 3 tests with `@pytest.mark.skip(reason="Phase 3 not implemented")`
- **Test isolation**: Use fixtures to reset thresholds/timers between tests
- **Entity IDs**: Match exactly with `esphome/packages/presence_engine.yaml`
- **Documentation sync**: When adding new tests, update this file and `docs/ARCHITECTURE.md`

### Common Test Patterns
```python
# Poll for state change with timeout
async def wait_for_state(client, entity_id, expected_state, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        state = await client.get_state(entity_id)
        if state == expected_state:
            return True
        await asyncio.sleep(0.5)
    return False

# Reset device to known state
@pytest.fixture
async def reset_defaults(ha_client):
    await ha_client.call_service(
        "esphome", "bed_presence_detector_reset_to_defaults"
    )
    await asyncio.sleep(1)  # Allow service to complete
```

### Adding New Tests
When firmware behavior changes:
1. Update test assertions to match new defaults
2. Add tests for new entities (e.g., Phase 3 calibration helpers)
3. Update entity ID constants if names change
4. Update this AGENTS.md file with new test scope
5. Update `docs/ARCHITECTURE.md` testing section

## Troubleshooting

### Connection Issues
- **"Connection refused"**:
  - Verify running on ubuntu-node (NOT Codespaces)
  - Check `~/.env.local` has correct HA_URL and HA_TOKEN
  - Test HA WebSocket: `wscat -c ws://192.168.0.148:8123/api/websocket`
  - Confirm Home Assistant is running and accessible
- **"Authentication failed"**:
  - Regenerate long-lived access token in HA UI
  - Update `~/.env.local` with new token
  - Ensure token has admin privileges

### Entity Issues
- **"Entity not found"**:
  - Confirm ESPHome device online in HA UI
  - Check entity IDs match `esphome/packages/presence_engine.yaml`
  - Verify firmware has been flashed with Phase 2 code
  - Look for typos in entity ID strings (common: underscores vs hyphens)
- **"Entity state unexpected"**:
  - Check ESPHome device logs: `esphome logs bed-presence-detector.yaml`
  - Verify baseline calibration is correct
  - Reset device to defaults before test run

### Service Issues
- **"Service call failed"**:
  - Check ESPHome logs for error messages
  - Verify service names match `packages/services_calibration.yaml`
  - Remember: Phase 3 services (start/stop_calibration) only log messages
- **"Timeout waiting for service response"**:
  - Increase timeout in test
  - Check device isn't busy processing previous request
  - Verify device WiFi connection is stable

### Test Failures
- **Flaky tests**: Increase debounce timers or polling intervals
- **Defaults mismatch**: Check firmware was compiled with latest thresholds
- **Phase 3 tests running**: Ensure `@pytest.mark.skip` decorator present

For broader context, see `../../AGENTS.md`. For firmware issues, see `../../esphome/AGENTS.md`.
