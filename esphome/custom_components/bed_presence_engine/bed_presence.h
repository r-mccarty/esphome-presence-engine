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

  // Hardcoded baseline statistics (UPDATE THESE after baseline collection)
  // TODO: Replace these placeholder values with actual baseline data from your LD2410 sensor
  // To collect baseline: Run sensor for 30-60s in empty bed, observe moving/static energy values
  float mu_move_{100.0f};   // Mean moving energy (placeholder)
  float sigma_move_{20.0f}; // Std dev moving energy (placeholder)
  float mu_stat_{100.0f};   // Mean static energy (placeholder)
  float sigma_stat_{20.0f}; // Std dev static energy (placeholder)

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
