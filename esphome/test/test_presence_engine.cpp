/**
 * Unit Tests for Bed Presence Engine - Phase 1
 *
 * These tests document and verify Phase 1 z-score logic behavior.
 * Since the actual implementation requires ESPHome dependencies,
 * these tests demonstrate the expected behavior using a simplified model.
 */

#include <gtest/gtest.h>
#include <cmath>
#include <string>

/**
 * Simplified Phase 1 Presence Engine for Testing
 *
 * This models the core Phase 1 logic without ESPHome dependencies:
 * - Z-score calculation
 * - Simple threshold comparison with hysteresis
 * - No debouncing or temporal filtering
 */
class SimplePresenceEngine {
public:
    // Configuration (matching actual implementation defaults)
    float mu_move_ = 100.0f;
    float sigma_move_ = 20.0f;
    float k_on_ = 4.0f;
    float k_off_ = 2.0f;

    // State
    bool is_occupied_ = false;
    std::string last_reason_ = "";

    // Z-score calculation: z = (x - μ) / σ
    float calculate_z_score(float energy) {
        if (sigma_move_ <= 0.001f) {
            return 0.0f;  // Prevent division by zero
        }
        return (energy - mu_move_) / sigma_move_;
    }

    // Process energy reading (Phase 1 logic)
    void process_energy(float energy) {
        float z = calculate_z_score(energy);

        if (!is_occupied_ && z > k_on_) {
            is_occupied_ = true;
            char buf[64];
            snprintf(buf, sizeof(buf), "ON: z=%.2f > k_on=%.2f", z, k_on_);
            last_reason_ = buf;
        }
        else if (is_occupied_ && z < k_off_) {
            is_occupied_ = false;
            char buf[64];
            snprintf(buf, sizeof(buf), "OFF: z=%.2f < k_off=%.2f", z, k_off_);
            last_reason_ = buf;
        }
    }
};

class PresenceEngineTest : public ::testing::Test {
protected:
    SimplePresenceEngine engine_;
};

TEST_F(PresenceEngineTest, ZScoreCalculation) {
    // With μ=100, σ=20:
    EXPECT_FLOAT_EQ(engine_.calculate_z_score(100.0f), 0.0f);   // (100-100)/20 = 0
    EXPECT_FLOAT_EQ(engine_.calculate_z_score(120.0f), 1.0f);   // (120-100)/20 = 1
    EXPECT_FLOAT_EQ(engine_.calculate_z_score(140.0f), 2.0f);   // (140-100)/20 = 2
    EXPECT_FLOAT_EQ(engine_.calculate_z_score(180.0f), 4.0f);   // (180-100)/20 = 4
    EXPECT_FLOAT_EQ(engine_.calculate_z_score(80.0f), -1.0f);   // (80-100)/20 = -1
}

TEST_F(PresenceEngineTest, InitialStateIsVacant) {
    EXPECT_FALSE(engine_.is_occupied_);
}

TEST_F(PresenceEngineTest, TransitionsToOccupiedAboveKOn) {
    // k_on=4.0, so need z>4
    // z=4 means energy = 100 + 4*20 = 180

    engine_.process_energy(180.0f);  // z=4.0, exactly at threshold
    EXPECT_FALSE(engine_.is_occupied_);  // Should be OFF (need >4, not >=4)

    engine_.process_energy(181.0f);  // z=4.05, above threshold
    EXPECT_TRUE(engine_.is_occupied_);   // Should turn ON
}

TEST_F(PresenceEngineTest, TransitionsToVacantBelowKOff) {
    // Turn ON first
    engine_.process_energy(185.0f);  // z=4.25
    EXPECT_TRUE(engine_.is_occupied_);

    // k_off=2.0, so need z<2 to turn OFF
    // z=2 means energy = 100 + 2*20 = 140

    engine_.process_energy(140.0f);  // z=2.0, exactly at threshold
    EXPECT_TRUE(engine_.is_occupied_);  // Should stay ON (need <2, not <=2)

    engine_.process_energy(135.0f);  // z=1.75, below threshold
    EXPECT_FALSE(engine_.is_occupied_);  // Should turn OFF
}

TEST_F(PresenceEngineTest, HysteresisPreventsFalseNegatives) {
    // Hysteresis zone is between k_off and k_on (2.0 to 4.0)

    engine_.process_energy(185.0f);  // z=4.25, turn ON
    EXPECT_TRUE(engine_.is_occupied_);

    // Energy drops to hysteresis zone (z=3, between k_off and k_on)
    engine_.process_energy(160.0f);  // z=3.0
    EXPECT_TRUE(engine_.is_occupied_);  // Should remain ON

    // Only turns OFF when below k_off
    engine_.process_energy(135.0f);  // z=1.75 < k_off
    EXPECT_FALSE(engine_.is_occupied_);
}

TEST_F(PresenceEngineTest, NoDebouncing) {
    // Phase 1: State changes are immediate (no temporal filtering)

    // Immediate ON
    EXPECT_FALSE(engine_.is_occupied_);
    engine_.process_energy(185.0f);  // Above k_on
    EXPECT_TRUE(engine_.is_occupied_);  // Should change immediately

    // Immediate OFF
    engine_.process_energy(135.0f);  // Below k_off
    EXPECT_FALSE(engine_.is_occupied_);  // Should change immediately

    // Can oscillate rapidly (this is the "twitchy" behavior Phase 1 expects)
    engine_.process_energy(185.0f);
    EXPECT_TRUE(engine_.is_occupied_);
    engine_.process_energy(135.0f);
    EXPECT_FALSE(engine_.is_occupied_);
    engine_.process_energy(185.0f);
    EXPECT_TRUE(engine_.is_occupied_);
}

TEST_F(PresenceEngineTest, UpdateKOnDynamically) {
    engine_.k_on_ = 5.0f;  // Increase threshold

    // Now need z>5, so energy > 100 + 5*20 = 200
    engine_.process_energy(185.0f);  // z=4.25 < k_on
    EXPECT_FALSE(engine_.is_occupied_);

    engine_.process_energy(205.0f);  // z=5.25 > k_on
    EXPECT_TRUE(engine_.is_occupied_);
}

TEST_F(PresenceEngineTest, UpdateKOffDynamically) {
    // Turn ON first
    engine_.process_energy(185.0f);
    EXPECT_TRUE(engine_.is_occupied_);

    // Update k_off to 3.0
    engine_.k_off_ = 3.0f;

    // Now need z<3 to turn OFF, so energy < 100 + 3*20 = 160
    engine_.process_energy(165.0f);  // z=3.25 > k_off
    EXPECT_TRUE(engine_.is_occupied_);  // Should remain ON

    engine_.process_energy(155.0f);  // z=2.75 < k_off
    EXPECT_FALSE(engine_.is_occupied_);  // Should turn OFF
}

TEST_F(PresenceEngineTest, StateReasonIsUpdated) {
    // Turn ON
    engine_.process_energy(185.0f);
    EXPECT_NE(engine_.last_reason_.find("ON:"), std::string::npos);
    EXPECT_NE(engine_.last_reason_.find("z="), std::string::npos);
    std::string reason_on = engine_.last_reason_;

    // Turn OFF
    engine_.process_energy(135.0f);
    EXPECT_NE(engine_.last_reason_.find("OFF:"), std::string::npos);
    EXPECT_NE(engine_.last_reason_.find("z="), std::string::npos);

    // Reasons should be different
    EXPECT_NE(reason_on, engine_.last_reason_);
}

TEST_F(PresenceEngineTest, HandlesZeroSigmaGracefully) {
    engine_.sigma_move_ = 0.0f;

    // Should return z=0 without crashing
    EXPECT_FLOAT_EQ(engine_.calculate_z_score(100.0f), 0.0f);
    EXPECT_FLOAT_EQ(engine_.calculate_z_score(1000.0f), 0.0f);

    // Should not change state (z=0 is between k_off and k_on)
    engine_.process_energy(1000.0f);
    EXPECT_FALSE(engine_.is_occupied_);
}

TEST_F(PresenceEngineTest, HandlesNegativeEnergyValues) {
    // Negative energy should work (could happen with sensor noise)
    engine_.process_energy(-40.0f);  // z = (-40-100)/20 = -7
    EXPECT_FALSE(engine_.is_occupied_);  // Should remain OFF

    // Should still be able to turn ON with high values
    engine_.process_energy(185.0f);
    EXPECT_TRUE(engine_.is_occupied_);
}

TEST_F(PresenceEngineTest, HandlesVeryLargeEnergyValues) {
    // Very large energy should turn ON
    engine_.process_energy(10000.0f);  // z = (10000-100)/20 = 495
    EXPECT_TRUE(engine_.is_occupied_);

    // And back OFF with low values
    engine_.process_energy(0.0f);  // z = (0-100)/20 = -5
    EXPECT_FALSE(engine_.is_occupied_);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
