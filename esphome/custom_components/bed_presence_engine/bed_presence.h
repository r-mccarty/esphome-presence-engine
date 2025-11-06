#pragma once

#include "esphome/core/component.h"
#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/text_sensor/text_sensor.h"

namespace esphome {
namespace bed_presence_engine {

/**
 * BedPresenceEngine Component - Phase 1 Implementation
 *
 * Implements simple z-score based presence detection:
 * - Calculates z-score: z = (energy - μ) / σ
 * - Compares against threshold multipliers k_on and k_off
 * - No debouncing or state machine (intentionally "twitchy")
 * - Validates the core statistical significance concept
 */
class BedPresenceEngine : public Component, public binary_sensor::BinarySensor {
 public:
  void setup() override;
  void loop() override;
  float get_setup_priority() const override { return setup_priority::DATA; }

  // Configuration setters
  void set_energy_sensor(sensor::Sensor *sensor) { energy_sensor_ = sensor; }
  void set_k_on(float k) { k_on_ = k; }
  void set_k_off(float k) { k_off_ = k; }
  void set_state_reason_sensor(text_sensor::TextSensor *sensor) { state_reason_sensor_ = sensor; }

  // Public methods for runtime updates from HA
  void update_k_on(float k);
  void update_k_off(float k);

 protected:
  // Input sensor
  sensor::Sensor *energy_sensor_{nullptr};

  // Baseline calibration collected on 2025-11-05 22:36:52
  // Location: Right nightstand, Queen bed, sensor aimed at bed center
  // Conditions: Empty bed, door closed, user 25-30ft away
  // Statistics: mean=6.30%, stdev=2.56%, n=30 samples over 60 seconds
  float mu_move_{6.3f};     // Mean still energy (empty bed)
  float sigma_move_{2.6f};  // Std dev still energy (empty bed)
  float mu_stat_{6.3f};     // Same as mu_move_ for Phase 1
  float sigma_stat_{2.6f};  // Same as sigma_move_ for Phase 1

  // Threshold multipliers (k_on > k_off for hysteresis)
  float k_on_{4.0f};   // Turn ON when z > k_on (default: 4 std deviations)
  float k_off_{2.0f};  // Turn OFF when z < k_off (default: 2 std deviations)

  // Current state (simple boolean for Phase 1)
  bool is_occupied_{false};

  // Output sensors
  text_sensor::TextSensor *state_reason_sensor_{nullptr};

  // Internal methods
  float calculate_z_score(float energy, float mu, float sigma);
  void process_energy_reading(float energy);
  void publish_reason(const char *reason);
};

}  // namespace bed_presence_engine
}  // namespace esphome
