# AGENTS.md - End-to-End Integration Tests

This file provides guidance for AI agents working with Python-based E2E integration tests for the bed presence detection system.

## Overview

This directory contains Python-based End-to-End (E2E) integration tests that verify the complete system works correctly with a live Home Assistant instance. These tests complement the C++ unit tests by validating the full integration stack.

**Important**: These tests require a **live Home Assistant instance** with a connected bed presence detector device.

## Directory Structure

```
tests/e2e/
├── test_calibration_flow.py    # Integration tests for HA entities and services
├── requirements.txt             # Python dependencies
└── README.md                    # Test execution instructions (if exists)
```

## Quick Commands (run from this directory)

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export HA_URL="ws://homeassistant.local:8123/api/websocket"
export HA_TOKEN="your-long-lived-access-token"

# Run all tests
pytest

# Run specific test function
pytest test_calibration_flow.py::test_threshold_entities_exist

# Run with verbose output
pytest -v

# Run with output capture disabled (see print statements)
pytest -s

# Run only non-skipped tests (Phase 1 tests)
pytest -k "not calibration"
```

## Dependencies (requirements.txt)

Current dependencies (Phase 1):
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
homeassistant-api>=4.0.0
```

**Key libraries**:
- `pytest`: Testing framework
- `pytest-asyncio`: Support for async test functions
- `homeassistant-api`: WebSocket client for Home Assistant API

## Test File Structure

### test_calibration_flow.py

**Status**: ✅ Phase 1 tests functional, Phase 3 tests marked as skipped

**Test functions**:

#### Phase 1 Tests (Functional)
```python
def test_threshold_entities_exist():
    """Verify k_on and k_off entities exist"""
    # Checks: number.k_on_on_threshold_multiplier
    # Checks: number.k_off_off_threshold_multiplier

def test_threshold_values_are_correct():
    """Verify default threshold values (4.0, 2.0)"""

def test_update_threshold_via_service():
    """Verify threshold can be changed via HA service call"""

def test_reset_to_defaults():
    """Verify reset service restores defaults"""
    # Tests: esphome.bed_presence_detector_reset_to_defaults
```

#### Phase 3 Tests (Skipped)
```python
@pytest.mark.skip(reason="Phase 3 feature - not yet implemented")
def test_calibration_helpers_exist():
    """Verify helper entities for calibration wizard"""
    # Will check: input_boolean.bed_presence_calibrating
    # Will check: input_number.calibration_duration
    # Will check: input_text.calibration_status

@pytest.mark.skip(reason="Phase 3 feature - not yet implemented")
def test_full_calibration_flow():
    """Test complete calibration workflow"""
    # Will test: start_calibration → collect data → calculate stats → update thresholds
```

## Running Tests

### Prerequisites

1. **Home Assistant Instance**: Running and accessible
2. **ESPHome Integration**: Installed in HA
3. **Bed Presence Device**: Connected and online
4. **Long-Lived Access Token**: Generated in HA user profile

### Generating a Long-Lived Access Token

1. In Home Assistant web UI: Click your profile (bottom left)
2. Scroll to "Long-Lived Access Tokens" section
3. Click "Create Token"
4. Give it a name (e.g., "E2E Test Access")
5. Copy the token (it won't be shown again!)
6. Export to environment: `export HA_TOKEN="your-token-here"`

### Setting Up Environment

```bash
cd tests/e2e

# Install dependencies
pip install -r requirements.txt

# Set Home Assistant URL
export HA_URL="ws://homeassistant.local:8123/api/websocket"
# OR if using IP address:
export HA_URL="ws://192.168.1.100:8123/api/websocket"

# Set access token
export HA_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Your token

# Verify connection
pytest test_calibration_flow.py::test_threshold_entities_exist -v
```

### Expected Test Output (Phase 1)

```
============================= test session starts =============================
platform linux -- Python 3.11.0, pytest-7.4.0, pluggy-1.3.0
collected 6 items

test_calibration_flow.py::test_threshold_entities_exist PASSED          [ 16%]
test_calibration_flow.py::test_threshold_values_are_correct PASSED      [ 33%]
test_calibration_flow.py::test_update_threshold_via_service PASSED      [ 50%]
test_calibration_flow.py::test_reset_to_defaults PASSED                 [ 66%]
test_calibration_flow.py::test_calibration_helpers_exist SKIPPED        [ 83%]
test_calibration_flow.py::test_full_calibration_flow SKIPPED            [100%]

======================== 4 passed, 2 skipped in 2.34s ========================
```

**All Phase 1 tests should pass. Phase 3 tests are skipped.**

## Writing New E2E Tests

### Test Function Template

```python
import pytest
from homeassistant_api import Client

def test_new_feature():
    """Test description here"""
    # 1. Connect to Home Assistant
    client = Client(
        api_url=os.getenv("HA_URL"),
        token=os.getenv("HA_TOKEN")
    )

    # 2. Get entity state
    entity = client.get_state(entity_id="sensor.some_sensor")

    # 3. Assert expected state
    assert entity.state == "expected_value"

    # 4. Call service (if needed)
    client.trigger_service(
        domain="esphome",
        service="bed_presence_detector_some_service"
    )

    # 5. Wait for state change
    import time
    time.sleep(2)

    # 6. Verify new state
    updated_entity = client.get_state(entity_id="sensor.some_sensor")
    assert updated_entity.state == "new_value"
```

### Async Test Function Template

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_operation():
    """Test async operations"""
    client = Client(...)

    # Async operation
    await asyncio.sleep(1)

    # Test logic here
    entity = client.get_state(entity_id="...")
    assert entity.state == "expected"
```

### Testing Service Calls

```python
def test_service_call():
    """Test ESPHome service invocation"""
    client = Client(...)

    # Call service
    client.trigger_service(
        domain="esphome",
        service="bed_presence_detector_reset_to_defaults"
    )

    # Wait for service to complete
    time.sleep(1)

    # Verify results
    k_on = client.get_state(entity_id="number.k_on_on_threshold_multiplier")
    assert float(k_on.state) == 4.0  # Default value
```

### Testing Entity State Changes

```python
def test_threshold_update():
    """Test that changing threshold updates entity state"""
    client = Client(...)

    # Get initial state
    initial = client.get_state(entity_id="number.k_on_on_threshold_multiplier")
    initial_value = float(initial.state)

    # Update via service
    client.trigger_service(
        domain="number",
        service="set_value",
        service_data={
            "entity_id": "number.k_on_on_threshold_multiplier",
            "value": 5.0
        }
    )

    # Wait for update
    time.sleep(0.5)

    # Verify change
    updated = client.get_state(entity_id="number.k_on_on_threshold_multiplier")
    assert float(updated.state) == 5.0
    assert float(updated.state) != initial_value
```

## Common Test Patterns

### Entity Existence Check
```python
def test_entity_exists():
    client = Client(...)
    entity = client.get_state(entity_id="binary_sensor.bed_occupied")
    assert entity is not None
    assert entity.state in ["on", "off"]  # Valid binary sensor states
```

### Entity Attribute Check
```python
def test_entity_attributes():
    client = Client(...)
    entity = client.get_state(entity_id="number.k_on_on_threshold_multiplier")

    assert "min" in entity.attributes
    assert "max" in entity.attributes
    assert entity.attributes["min"] == 0.0
    assert entity.attributes["max"] == 10.0
```

### Service Availability Check
```python
def test_service_exists():
    client = Client(...)
    services = client.get_services()

    assert "esphome" in services
    assert "bed_presence_detector_reset_to_defaults" in services["esphome"]
```

### Time-Based Testing
```python
def test_state_change_timing():
    """Test that state changes occur within expected timeframe"""
    client = Client(...)

    # Record start time
    start_time = time.time()

    # Trigger action
    client.trigger_service(...)

    # Poll for state change (with timeout)
    max_wait = 5.0  # seconds
    while time.time() - start_time < max_wait:
        entity = client.get_state(entity_id="...")
        if entity.state == "expected_state":
            break
        time.sleep(0.1)
    else:
        pytest.fail(f"State did not change within {max_wait} seconds")

    # Verify timing
    elapsed = time.time() - start_time
    assert elapsed < 2.0  # Should happen quickly
```

## Phase-Specific Testing

### Phase 1 Tests (Current)
**Focus**: Entity existence, threshold updates, basic service calls

**Test coverage**:
- ✅ Threshold entities exist with correct names
- ✅ Default values are correct (4.0, 2.0)
- ✅ Thresholds can be updated via service calls
- ✅ Reset service restores defaults
- ✅ Presence state entity exists and reports valid states

**What NOT to test in Phase 1**:
- ❌ Debounce behavior (Phase 2 feature)
- ❌ State machine transitions (Phase 2 feature)
- ❌ Calibration workflow (Phase 3 feature)
- ❌ Distance windowing (Phase 3 feature)

### Phase 2 Tests (Planned)
**Focus**: State machine transitions, debounce timing

**Example tests to add**:
```python
def test_state_machine_transitions():
    """Verify state transitions through IDLE → DEBOUNCING_ON → PRESENT"""
    # Will require new entity: sensor.presence_state_machine
    # Test: Check state transitions with timing

def test_debounce_on_prevents_false_positives():
    """Verify brief signals don't trigger occupied state"""
    # Simulate brief energy spike
    # Verify state stays vacant due to debounce timer

def test_debounce_off_prevents_false_negatives():
    """Verify brief drops don't trigger vacant state"""
    # Simulate brief energy drop while occupied
    # Verify state stays occupied due to debounce timer
```

### Phase 3 Tests (Planned)
**Focus**: Calibration workflow, automated statistics

**Example tests to add**:
```python
def test_calibration_collects_baseline_data():
    """Verify calibration service collects data for specified duration"""
    # Call start_calibration service with duration=30
    # Wait 30 seconds
    # Verify calibration completed
    # Check that new μ and σ values were calculated

def test_calibration_updates_thresholds():
    """Verify calibration automatically updates threshold values"""
    # Record initial thresholds
    # Run calibration
    # Verify thresholds changed based on new statistics

def test_distance_windowing():
    """Verify distance window filters out-of-range detections"""
    # Set d_min_cm and d_max_cm
    # Simulate detections outside window
    # Verify they're ignored
```

## Troubleshooting E2E Tests

### Connection Errors

**Error**: `ConnectionRefusedError: [Errno 111] Connection refused`

**Causes**:
- Home Assistant not running
- Wrong URL (check IP address or hostname)
- Wrong port (default: 8123)
- Firewall blocking connection

**Fixes**:
```bash
# Verify HA is accessible
curl http://homeassistant.local:8123

# Check environment variable
echo $HA_URL
# Should output: ws://homeassistant.local:8123/api/websocket

# Try IP address instead of hostname
export HA_URL="ws://192.168.1.100:8123/api/websocket"
```

### Authentication Errors

**Error**: `Unauthorized: Invalid access token`

**Causes**:
- Token expired or revoked
- Wrong token copied
- Token not exported to environment

**Fixes**:
```bash
# Check environment variable
echo $HA_TOKEN
# Should output your long token string

# Re-export token (check for copy/paste errors)
export HA_TOKEN="eyJhbGc..."

# Generate new token in HA if needed
```

### Entity Not Found Errors

**Error**: `Entity not found: number.k_on_on_threshold_multiplier`

**Causes**:
- Device not connected to Home Assistant
- Wrong entity ID in test
- Device named differently than expected

**Fixes**:
1. Check device is online: Settings → Devices & Services → ESPHome
2. Verify entity IDs: Click device → See all entities
3. Copy exact entity ID from HA UI
4. Update test to use correct entity ID

### Test Timeout Errors

**Error**: Test hangs or times out

**Causes**:
- Waiting for state change that never happens
- Network latency
- Home Assistant processing slowly

**Fixes**:
```python
# Add timeout to prevent hanging
@pytest.mark.timeout(10)  # Requires pytest-timeout
def test_with_timeout():
    # Test code here
    pass

# Add explicit timeouts to waits
max_wait = 5.0
start = time.time()
while time.time() - start < max_wait:
    # Check condition
    if condition_met:
        break
    time.sleep(0.1)
else:
    pytest.fail("Timeout waiting for condition")
```

## Best Practices for E2E Tests

### 1. Keep Tests Independent
Each test should:
- Not depend on other tests running first
- Clean up after itself (restore original state)
- Not assume specific starting state

**Good**:
```python
def test_feature():
    # Save original state
    original = client.get_state(...)

    # Test logic
    # ...

    # Restore original state
    client.trigger_service(... restore original ...)
```

**Bad**:
```python
def test_part_1():
    # Changes state
    pass

def test_part_2():
    # Assumes state from test_part_1
    # BRITTLE - will fail if test_part_1 skipped
    pass
```

### 2. Use Descriptive Test Names
```python
# Good
def test_occupied_threshold_prevents_false_positives_below_k_on():
    pass

# Bad
def test_threshold():
    pass
```

### 3. Add Helpful Failure Messages
```python
# Good
assert float(entity.state) == 4.0, \
    f"Expected k_on=4.0, got {entity.state}. Check if reset service worked."

# Bad
assert float(entity.state) == 4.0
```

### 4. Minimize Test Duration
- Use short timeouts where appropriate
- Don't sleep longer than necessary
- Skip slow tests in CI if needed

```python
@pytest.mark.slow  # Mark slow tests
def test_long_calibration():
    # Test that takes >30 seconds
    pass

# Run fast tests only:
# pytest -m "not slow"
```

### 5. Handle Flakiness
E2E tests can be flaky due to timing, network, etc.

**Strategies**:
- Add retries for transient failures
- Use polling instead of fixed sleeps
- Add generous timeouts
- Mark known-flaky tests

```python
def test_with_retry():
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Test logic
            entity = client.get_state(...)
            assert entity.state == "expected"
            break
        except AssertionError:
            if attempt == max_attempts - 1:
                raise  # Final attempt, let it fail
            time.sleep(1)  # Wait before retry
```

## CI/CD Integration

### Running Tests in GitHub Actions

**Current status**: E2E tests are NOT run in CI (require live HA instance)

**Future**: Add workflow for E2E tests against test HA instance

```yaml
# Example: .github/workflows/e2e_tests.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd tests/e2e
          pip install -r requirements.txt
      - name: Run E2E tests
        env:
          HA_URL: ${{ secrets.TEST_HA_URL }}
          HA_TOKEN: ${{ secrets.TEST_HA_TOKEN }}
        run: |
          cd tests/e2e
          pytest -v
```

**Requirements for CI E2E tests**:
- Dedicated test Home Assistant instance
- Test bed presence device (or mock)
- Secure storage of HA_TOKEN in GitHub secrets

## Mock Testing vs Live Testing

### Live Testing (Current Approach)
**Pros**:
- Tests real integration
- Catches actual bugs
- Validates full stack

**Cons**:
- Requires live HA instance
- Slower than unit tests
- Can be flaky

### Mock Testing (Alternative)
**Pros**:
- Fast execution
- No external dependencies
- Deterministic

**Cons**:
- Doesn't test real integration
- Mocks can diverge from reality

**Recommendation**: Use both
- Live tests for critical user flows (Phase 1+)
- Mock tests for edge cases and error handling

## Test Data Management

### Using Test Fixtures

```python
import pytest
from homeassistant_api import Client

@pytest.fixture
def ha_client():
    """Fixture providing configured HA client"""
    return Client(
        api_url=os.getenv("HA_URL"),
        token=os.getenv("HA_TOKEN")
    )

@pytest.fixture
def reset_thresholds(ha_client):
    """Fixture that resets thresholds before/after test"""
    # Reset before test
    ha_client.trigger_service(
        domain="esphome",
        service="bed_presence_detector_reset_to_defaults"
    )
    yield  # Run test
    # Reset after test
    ha_client.trigger_service(
        domain="esphome",
        service="bed_presence_detector_reset_to_defaults"
    )

def test_with_fixtures(ha_client, reset_thresholds):
    """Test automatically gets reset thresholds"""
    entity = ha_client.get_state(entity_id="number.k_on_on_threshold_multiplier")
    assert float(entity.state) == 4.0
```

## Additional Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://github.com/pytest-dev/pytest-asyncio
- **Home Assistant REST API**: https://developers.home-assistant.io/docs/api/rest/
- **Home Assistant WebSocket API**: https://developers.home-assistant.io/docs/api/websocket/
- **homeassistant-api Library**: https://github.com/GrandMoff100/HomeAssistantAPI

---

**Need broader context?** See `../../CLAUDE.md` for comprehensive project documentation, or `../../AGENTS.md` for repository-wide agent guidance.
