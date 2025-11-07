#include "bed_presence.h"
#include "esphome/core/log.h"
#include <cmath>

namespace esphome {
namespace bed_presence_engine {

static const char *const TAG = "bed_presence_engine";

void BedPresenceEngine::setup() {
  ESP_LOGCONFIG(TAG, "Setting up Bed Presence Engine (Phase 2)...");
  ESP_LOGCONFIG(TAG, "  Baseline (still): μ=%.2f, σ=%.2f", this->mu_still_, this->sigma_still_);
  ESP_LOGCONFIG(TAG, "  Baseline (stat): μ=%.2f, σ=%.2f", this->mu_stat_, this->sigma_stat_);
  ESP_LOGCONFIG(TAG, "  Threshold multipliers: k_on=%.2f, k_off=%.2f", this->k_on_, this->k_off_);
  ESP_LOGCONFIG(TAG, "  Debounce timers: on=%lums, off=%lums, abs_clear=%lums",
                this->on_debounce_ms_, this->off_debounce_ms_, this->abs_clear_delay_ms_);
  ESP_LOGCONFIG(TAG, "  Phase 2: State machine with debouncing enabled");

  // Initialize to IDLE state
  this->current_state_ = IDLE;
  this->publish_state(false);

  if (this->state_reason_sensor_ != nullptr) {
    this->state_reason_sensor_->publish_state("Initial state: IDLE");
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
  // Calculate z-score for still energy (Phase 2 uses still_energy)
  float z_still = this->calculate_z_score(energy, this->mu_still_, this->sigma_still_);

  // Log the z-score for debugging
  ESP_LOGVV(TAG, "Energy=%.2f, z_still=%.2f, state=%d", energy, z_still, this->current_state_);

  unsigned long now = millis();

  // Phase 2 Logic: 4-state machine with debouncing
  switch (this->current_state_) {
    case IDLE:
      if (z_still >= this->k_on_) {
        this->debounce_start_time_ = now;
        this->current_state_ = DEBOUNCING_ON;
        ESP_LOGD(TAG, "IDLE → DEBOUNCING_ON (z=%.2f >= k_on=%.2f)", z_still, this->k_on_);
      }
      break;

    case DEBOUNCING_ON:
      if (z_still >= this->k_on_) {
        // Condition still holds, check timer
        if ((now - this->debounce_start_time_) >= this->on_debounce_ms_) {
          this->current_state_ = PRESENT;
          this->last_high_confidence_time_ = now;
          this->publish_state(true);

          char reason[64];
          snprintf(reason, sizeof(reason), "ON: z=%.2f, debounced %lums", z_still, this->on_debounce_ms_);
          this->publish_reason(reason);

          ESP_LOGI(TAG, "DEBOUNCING_ON → PRESENT: %s", reason);
        }
      } else {
        // Condition lost, abort debounce
        this->current_state_ = IDLE;
        ESP_LOGD(TAG, "DEBOUNCING_ON → IDLE (z=%.2f < k_on, abort)", z_still);
      }
      break;

    case PRESENT:
      // Update high confidence timestamp whenever strong signal detected
      if (z_still > this->k_on_) {
        this->last_high_confidence_time_ = now;
      }

      // Check for transition to DEBOUNCING_OFF
      if (z_still < this->k_off_) {
        // Low signal detected, check absolute clear delay
        if ((now - this->last_high_confidence_time_) >= this->abs_clear_delay_ms_) {
          this->debounce_start_time_ = now;
          this->current_state_ = DEBOUNCING_OFF;
          ESP_LOGD(TAG, "PRESENT → DEBOUNCING_OFF (z=%.2f < k_off, abs_clear=%lums ago)",
                   z_still, (now - this->last_high_confidence_time_));
        }
      }
      break;

    case DEBOUNCING_OFF:
      if (z_still < this->k_off_) {
        // Condition still holds, check timer
        if ((now - this->debounce_start_time_) >= this->off_debounce_ms_) {
          this->current_state_ = IDLE;
          this->publish_state(false);

          char reason[64];
          snprintf(reason, sizeof(reason), "OFF: z=%.2f, debounced %lums", z_still, this->off_debounce_ms_);
          this->publish_reason(reason);

          ESP_LOGI(TAG, "DEBOUNCING_OFF → IDLE: %s", reason);
        }
      } else if (z_still >= this->k_on_) {
        // High signal returned, abort debounce
        this->current_state_ = PRESENT;
        this->last_high_confidence_time_ = now;
        ESP_LOGD(TAG, "DEBOUNCING_OFF → PRESENT (z=%.2f >= k_on, signal returned)", z_still);
      }
      break;
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

void BedPresenceEngine::update_on_debounce_ms(unsigned long ms) {
  ESP_LOGI(TAG, "Updating on_debounce_ms: %lu -> %lu", this->on_debounce_ms_, ms);
  this->on_debounce_ms_ = ms;
}

void BedPresenceEngine::update_off_debounce_ms(unsigned long ms) {
  ESP_LOGI(TAG, "Updating off_debounce_ms: %lu -> %lu", this->off_debounce_ms_, ms);
  this->off_debounce_ms_ = ms;
}

void BedPresenceEngine::update_abs_clear_delay_ms(unsigned long ms) {
  ESP_LOGI(TAG, "Updating abs_clear_delay_ms: %lu -> %lu", this->abs_clear_delay_ms_, ms);
  this->abs_clear_delay_ms_ = ms;
}

}  // namespace bed_presence_engine
}  // namespace esphome
