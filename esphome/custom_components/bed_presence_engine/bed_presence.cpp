#include "bed_presence.h"
#include "esphome/core/log.h"
#include <cmath>

namespace esphome {
namespace bed_presence_engine {

static const char *const TAG = "bed_presence_engine";

void BedPresenceEngine::setup() {
  ESP_LOGCONFIG(TAG, "Setting up Bed Presence Engine (Phase 1)...");
  ESP_LOGCONFIG(TAG, "  Baseline (moving): μ=%.2f, σ=%.2f", this->mu_move_, this->sigma_move_);
  ESP_LOGCONFIG(TAG, "  Baseline (static): μ=%.2f, σ=%.2f", this->mu_stat_, this->sigma_stat_);
  ESP_LOGCONFIG(TAG, "  Threshold multipliers: k_on=%.2f, k_off=%.2f", this->k_on_, this->k_off_);
  ESP_LOGCONFIG(TAG, "  NOTE: Phase 1 has NO debouncing - expect twitchy behavior");

  // Initialize to vacant state
  this->is_occupied_ = false;
  this->publish_state(false);

  if (this->state_reason_sensor_ != nullptr) {
    this->state_reason_sensor_->publish_state("Initial state: vacant");
  }
}

void BedPresenceEngine::loop() {
  // Check if we have a valid energy reading
  if (this->energy_sensor_ == nullptr || !this->energy_sensor_->has_state()) {
    return;
  }

  float energy = this->energy_sensor_->state;
  this->process_energy_reading(energy);
}

float BedPresenceEngine::calculate_z_score(float energy, float mu, float sigma) {
  // Prevent division by zero
  if (sigma <= 0.001f) {
    ESP_LOGW(TAG, "Invalid sigma (%.2f), returning z=0", sigma);
    return 0.0f;
  }

  // z = (x - μ) / σ
  return (energy - mu) / sigma;
}

void BedPresenceEngine::process_energy_reading(float energy) {
  // Calculate z-score for moving energy (Phase 1 uses only moving energy per spec)
  float z_move = this->calculate_z_score(energy, this->mu_move_, this->sigma_move_);

  // Log the z-score for debugging
  ESP_LOGVV(TAG, "Energy=%.2f, z_move=%.2f", energy, z_move);

  // Phase 1 Logic: Simple threshold comparison with hysteresis
  if (!this->is_occupied_ && z_move > this->k_on_) {
    // Transition to OCCUPIED
    this->is_occupied_ = true;
    this->publish_state(true);

    char reason[64];
    snprintf(reason, sizeof(reason), "ON: z=%.2f > k_on=%.2f", z_move, this->k_on_);
    this->publish_reason(reason);

    ESP_LOGI(TAG, "Presence detected: %s", reason);
  }
  else if (this->is_occupied_ && z_move < this->k_off_) {
    // Transition to VACANT
    this->is_occupied_ = false;
    this->publish_state(false);

    char reason[64];
    snprintf(reason, sizeof(reason), "OFF: z=%.2f < k_off=%.2f", z_move, this->k_off_);
    this->publish_reason(reason);

    ESP_LOGI(TAG, "Presence cleared: %s", reason);
  }
}

void BedPresenceEngine::publish_reason(const char *reason) {
  if (this->state_reason_sensor_ != nullptr) {
    this->state_reason_sensor_->publish_state(reason);
  }
}

void BedPresenceEngine::update_k_on(float k) {
  ESP_LOGI(TAG, "Updating k_on: %.2f -> %.2f", this->k_on_, k);
  this->k_on_ = k;
}

void BedPresenceEngine::update_k_off(float k) {
  ESP_LOGI(TAG, "Updating k_off: %.2f -> %.2f", this->k_off_, k);
  this->k_off_ = k;
}

}  // namespace bed_presence_engine
}  // namespace esphome
