# **On Device Presence Engine Spec**

### **Prerequisites & Environment**

* **Hardware:** M5Stack Basic v2.7 successfully connected to an LD2410C sensor via UART.  
* **Firmware Base:** ESPHome `v2025.11.0` or later. The device is flashed with a baseline configuration that successfully connects to Wi-Fi and Home Assistant.  
* **Comms:** The `ld2410` component is loaded in ESPHome, and basic sensors (e.g., `ld2410_presence`, `ld2410_moving_distance`) are reporting data to Home Assistant.  
* **Development Environment:** A setup capable of compiling ESPHome firmware, including the ability to edit and include custom C++ components (`external_components`).  
* **Testing Framework:** A combination of manual E2E tests via the Home Assistant UI and automated unit tests for the C++ code (using a framework like GoogleTest or PlatformIO's native testing).

---

### **Phase 1: Foundational Logic \- From Energy to Binary State**

**Objective:** Implement the most basic, non-filtered presence detection logic. The goal is to establish the core data pipeline and a single, testable threshold mechanism. This phase prioritizes simplicity to validate the core concept.

#### **Engineering Requirements:**

1. **Global Variables:** Define global variables within ESPHome for a static baseline (`μ_move`, `μ_stat`) and standard deviation (`σ_move`, `σ_stat`). These will be hardcoded initially.  
2. **Z-Score Calculation:** For every frame from the sensor, calculate the "z-score" for both moving and static energy. This normalizes the energy reading into a measure of statistical significance.  
   * `z_move = (current_moving_energy - μ_move) / σ_move`  
3. **Threshold Knobs:** Expose two `number` entities to Home Assistant: `k_on` and `k_off`. These will be multipliers for the z-score. They must be persistent across reboots (`restore_value: true`).  
4. **Core Binary Sensor:** Create a single `binary_sensor.bed_present` that turns ON when `z_move > k_on` and OFF when `z_move < k_off`.

#### **Implementation Plan (ESPHome YAML & Custom Component):**

This logic is too complex for a simple `lambda` filter; it requires a custom C++ component.

1. **Create Custom Component Structure:**  
   * `/esphome/custom_components/bed_presence/`  
   * `bed_presence.h`, `bed_presence.cpp`, `__init__.py`  
2. **`bed_presence.h` (C++ Header):**  
   * Define a `BedPresenceSensor` class that inherits from `esphome::Component`.  
   * Declare member variables for the pointers to the LD2410 moving/static energy sensors.  
   * Declare pointers to the `k_on` and `k_off` `number` entities.  
   * Declare a `binary_sensor` to publish the state.  
3. **`__init__.py` (ESPHome Config Schema):**  
   * Define the ESPHome YAML configuration schema. This will allow users to link the LD2410 sensors and create the `k_on`/`k_off` knobs.  
4. **`bed_presence.cpp` (C++ Implementation):**  
   * In the `setup()` method, get the pointers to the sensors and numbers defined in the YAML.  
   * In the `loop()` method (or by attaching a listener to the sensor), read the latest energy values.  
   * Implement the z-score calculation using hardcoded `mu` and `sigma` values.  
   * Implement the simple `if (z_move > k_on)` logic and publish the state to the binary sensor.

#### **Testing & Validation:**

* **Unit Test (Conceptual/C++):**  
  * **Given:** A set of simulated energy readings and hardcoded `mu=100`, `sigma=10`, `k_on=4.0`, `k_off=2.0`.  
  * **When:** The `loop()` method processes an energy reading of `150` (z-score of 5.0).  
  * **Then:** The binary sensor state must be published as `ON`.  
  * **When:** The `loop()` method processes an energy reading of `110` (z-score of 1.0).  
  * **Then:** The binary sensor state must be published as `OFF`.  
* **E2E Integration Test:**  
  1. Flash the firmware to the M5Stack.  
  2. In Home Assistant, set `k_on` to 4.0 and `k_off` to 2.0.  
  3. Move your hand in front of the sensor. **Observe:** The `bed_present` sensor turns ON.  
  4. Remain perfectly still or move away. **Observe:** The `bed_present` sensor turns OFF. The state should feel "twitchy" and hyper-responsive. This is the expected outcome for Phase 1\.

---

### **Phase 2: Temporal Filtering & State Management**

**Objective:** Eliminate the "twitchiness" by introducing time-based filtering (debouncing) and building a formal state machine. This is where the core reliability features from the CONOPS are built.

#### **Engineering Requirements:**

2. **State Machine:** The C++ component must be refactored to implement a simple state machine with three states: `IDLE`, `PRESENT`, and `CLEARING`.  
3. **On-Debounce:** The state can only transition from `IDLE` to `PRESENT` if the `z_move >= k_on` condition is met for a continuous duration defined by `on_debounce_ms`.  
4. **Off-Debounce & Absolute Clear:** The state can only transition from `PRESENT` to `CLEARING` if `z_move < k_off` for a continuous `off_debounce_ms` **AND** a separate `abs_clear_delay_ms` has elapsed since the last strong presence signal.  
5. **Tunable Debounce Knobs:** Expose `on_debounce_ms`, `off_debounce_ms`, and `abs_clear_delay_ms` as persistent `number` entities in Home Assistant.

#### **Implementation Plan (C++ Custom Component):**

1. **Refactor `BedPresenceSensor.h`:**  
   * Add an `enum State { IDLE, PRESENT, CLEARING };`  
   * Add member variables: `State current_state;`, `unsigned long last_trigger_time;`, `unsigned long last_state_change_time;`.  
2. **Refactor `BedPresenceSensor.cpp`:**  
   * The `loop()` method will now be a `switch (current_state)` statement.  
   * **Case `IDLE`:** Check if `z_move >= k_on`. If true, record the time. If `millis() - start_time > on_debounce_ms`, change state to `PRESENT`. If the condition becomes false, reset the timer.  
   * **Case `PRESENT`:** Check if `z_move < k_off`. If true, record the time. If the condition holds for `off_debounce_ms` AND `millis() - last_strong_presence_time > abs_clear_delay_ms`, change state to `CLEARING`. If `z_move` goes back above `k_on`, update `last_strong_presence_time`.  
   * **Case `CLEARING`:** This can be a transitional state that immediately moves to `IDLE` after publishing the `OFF` state, or it could have its own hold time if needed.  
   * Publish the binary sensor state only upon a state change.

#### **Testing & Validation:**

* **Unit Test (C++):**  
  * **Debounce On:** Simulate a stream of high z-scores lasting less than `on_debounce_ms`. **Assert:** The state remains `IDLE`. Then, provide a stream lasting longer than the debounce. **Assert:** The state transitions to `PRESENT`.  
  * **Debounce Off:** With the state in `PRESENT`, simulate a stream of low z-scores lasting less than `off_debounce_ms`. **Assert:** The state remains `PRESENT`.  
  * **Absolute Clear:** Test the `abs_clear_delay` logic by ensuring the state doesn't clear even after the off-debounce is met, if a strong signal was seen recently.  
* **E2E Integration Test:**  
  1. Flash the new firmware. Set `on_debounce` to 3000ms (3 seconds).  
  2. Quickly wave your hand in front of the sensor for 1 second. **Observe:** `bed_present` should **not** change state.  
  3. Hold your hand steady in front of the sensor for 4-5 seconds. **Observe:** `bed_present` should now turn ON. This confirms the on-debounce logic.  
  4. Test the clear delays similarly.

---

### **Phase 3: Environmental Hardening & Calibration Services**

**Objective:** Add advanced features that allow the sensor to adapt to its environment (distance windowing, fan filtering) and be controlled externally by the HA "Wizard" via services.

#### **Engineering Requirements:**

2. **Distance Windowing:** The component must read the `distance` value from the LD2410. Any frame whose distance is outside the `[d_min_cm, d_max_cm]` window shall be ignored by the presence logic.  
3. **Window Knobs:** Expose `d_min_cm` and `d_max_cm` as persistent `number` entities.  
4. **Baseline Calibration Service:** Create an ESPHome service `calibrate.start_baseline` that accepts a `duration_s`. When called, the device will collect energy data for that duration, calculate the `μ` and `σ` values using the MAD method, and store them internally.  
5. **Reason for Change:** Implement a `text_sensor.last_change_reason` that provides a human-readable string for why the state last changed (e.g., `on:threshold_exceeded`, `off:abs_clear_delay`).  
6. **Reset Service:** Create a `calibrate.reset_all` service that restores all knobs and calibration data to their "Known Good Default" values.

#### **Implementation Plan (C++ & YAML):**

1. **ESPHome YAML:**  
   * Define the new `number` entities for `d_min_cm` and `d_max_cm`.  
   * Define the services (`calibrate.start_baseline`, `calibrate.reset_all`) using the `services:` block in the component's config, linking them to C++ methods.  
2. **C++ Component:**  
   * Modify the component to get a pointer to the LD2410's distance sensor.  
   * At the top of the `loop()`, add the check: `if (distance < d_min_cm || distance > d_max_cm) { return; }`.  
   * Implement the `calibrate_baseline(int duration_s)` method. It will enter a temporary "calibrating" mode, collect all energy readings into a vector, and then use an algorithm to compute the median and MAD, saving the results.  
   * Implement the `reset_to_defaults()` method.  
   * Whenever a state transition occurs in the state machine, update an internal string variable and publish it to the `text_sensor`.

#### **Testing & Validation:**

* **Unit Test (C++):**  
  * Test the `calibrate_baseline` method with a known vector of data and assert the correct `mu` and `sigma` are calculated.  
  * Test the windowing logic by passing in sensor frames with distances both inside and outside the window and asserting that the state machine only reacts to the "inside" frames.  
* **E2E Integration Test:**  
  1. Place a box fan just outside the intended bed area. With windowing disabled, confirm the fan triggers the sensor.  
  2. Use the `number` entities to set a `d_min` and `d_max` that defines only the bed area and excludes the fan. **Observe:** The fan no longer triggers the `bed_present` sensor, but a person in the bed still does.  
  3. From Home Assistant's Developer Tools \-\> Services, call the `calibrate.start_baseline` service while the room is empty. **Observe:** The device logs should show the calibration process. The subsequent detection behavior should be more accurate for that specific room's noise profile.  
  4. Change a few knobs to weird values. Call the `calibrate.reset_all` service. **Observe:** The knobs in the HA UI should return to their default values.

