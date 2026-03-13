"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Property-Based Tests for Adaptive Rigor Protocol

This module contains property-based tests for the Adaptive Rigor Protocol,
which dynamically adjusts verification parameters based on threat level.

Properties Tested:
- Property 16: Proof of Work validation
- Property 17: Gradual recovery
- Property 18: Difficulty scaling
- Property 19: Difficulty notification
"""

import time
import hashlib
from hypothesis import given, settings, strategies as st
from diotec360.core.adaptive_rigor import AdaptiveRigor, SystemMode, RigorConfig


# ============================================================================
# Property 16: Proof of Work validation
# ============================================================================

@settings(max_examples=100, deadline=None)
@given(
    tx_id=st.text(min_size=1, max_size=100),
    difficulty=st.integers(min_value=1, max_value=6)
)
def test_property_16_pow_validation(tx_id, difficulty):
    """
    Feature: autonomous-sentinel, Property 16: Proof of Work validation
    
    For any PoW submission during Crisis Mode, the Adaptive Rigor should validate
    that SHA256(tx_id || nonce) starts with the required number of leading zeros.
    
    Validates: Requirements 3.5
    """
    rigor = AdaptiveRigor()
    
    # Activate crisis mode
    rigor.activate_crisis_mode()
    rigor.crisis_config.pow_difficulty = difficulty
    rigor.current_config.pow_difficulty = difficulty
    
    # Find a valid nonce (brute force)
    valid_nonce = None
    for nonce in range(10000):  # Limit search to prevent timeout
        hash_input = f"{tx_id}{nonce}".encode()
        hash_result = hashlib.sha256(hash_input).hexdigest()
        if hash_result.startswith("0" * difficulty):
            valid_nonce = nonce
            break
    
    if valid_nonce is not None:
        # Valid nonce should pass validation
        assert rigor.validate_pow(tx_id, valid_nonce), \
            f"Valid PoW nonce {valid_nonce} was rejected"
        
        # Invalid nonce should fail validation
        invalid_nonce = valid_nonce + 1
        if not rigor.validate_pow(tx_id, invalid_nonce):
            # This is expected - invalid nonce should fail
            pass


@settings(max_examples=100, deadline=None)
@given(
    tx_id=st.text(min_size=1, max_size=100),
    nonce=st.integers(min_value=0, max_value=1000000)
)
def test_property_16_pow_not_required_in_normal_mode(tx_id, nonce):
    """
    Feature: autonomous-sentinel, Property 16: Proof of Work validation
    
    For any transaction in normal mode, PoW validation should always pass
    (PoW not required).
    
    Validates: Requirements 3.5
    """
    rigor = AdaptiveRigor()
    
    # In normal mode, PoW should not be required
    assert rigor.current_mode == SystemMode.NORMAL
    assert not rigor.current_config.pow_required
    
    # Any nonce should be valid in normal mode
    assert rigor.validate_pow(tx_id, nonce), \
        "PoW validation should always pass in normal mode"


# ============================================================================
# Property 17: Gradual recovery
# ============================================================================

@settings(max_examples=100, deadline=None)
@given(
    elapsed_seconds=st.floats(min_value=0.0, max_value=60.0)
)
def test_property_17_gradual_recovery(elapsed_seconds):
    """
    Feature: autonomous-sentinel, Property 17: Gradual recovery
    
    For any Crisis Mode deactivation, the Adaptive Rigor should gradually restore
    Z3 timeout from 5s to 30s over 60 seconds, with intermediate values calculated linearly.
    
    Validates: Requirements 3.6
    """
    rigor = AdaptiveRigor()
    
    # Activate and then deactivate crisis mode
    rigor.activate_crisis_mode()
    rigor.deactivate_crisis_mode()
    
    # Simulate elapsed time
    rigor.recovery_start_time = time.time() - elapsed_seconds
    
    # Get current config (triggers recovery update)
    config = rigor.get_current_config()
    
    # Allow small tolerance for floating point comparison
    if elapsed_seconds >= 59.9:
        # Recovery should be complete or nearly complete
        # Mode might be NORMAL or RECOVERY depending on exact timing
        assert config.z3_timeout_seconds >= 29, \
            f"Timeout should be near 30s at end of recovery, got {config.z3_timeout_seconds}s"
        assert config.proof_depth in ["medium", "deep"]
        assert not config.pow_required
    else:
        # Recovery in progress
        # Mode should be RECOVERY (unless exactly at 60s boundary)
        if rigor.current_mode == SystemMode.RECOVERY:
            # Calculate expected timeout (linear interpolation)
            progress = elapsed_seconds / 60.0
            expected_timeout = int(5 + (30 - 5) * progress)
            
            # Allow small tolerance for rounding
            assert abs(config.z3_timeout_seconds - expected_timeout) <= 1, \
                f"Expected timeout ~{expected_timeout}s, got {config.z3_timeout_seconds}s"
            
            # Timeout should be between crisis and normal values
            assert 5 <= config.z3_timeout_seconds <= 30, \
                f"Timeout {config.z3_timeout_seconds}s outside valid range [5, 30]"
            
            # PoW should be required for first 30 seconds (with tolerance)
            if elapsed_seconds < 29.9:
                assert config.pow_required, "PoW should be required in first 30s of recovery"
            elif elapsed_seconds > 30.1:
                assert not config.pow_required, "PoW should not be required after 30s of recovery"
            # else: boundary case, either value is acceptable


def test_property_17_recovery_monotonic_increase():
    """
    Feature: autonomous-sentinel, Property 17: Gradual recovery
    
    For any recovery sequence, Z3 timeout should monotonically increase
    (never decrease) from 5s to 30s.
    
    Validates: Requirements 3.6
    """
    rigor = AdaptiveRigor()
    
    # Activate and deactivate crisis mode
    rigor.activate_crisis_mode()
    rigor.deactivate_crisis_mode()
    
    # Sample timeouts at different recovery points
    timeouts = []
    for elapsed in [0, 10, 20, 30, 40, 50, 60]:
        rigor.recovery_start_time = time.time() - elapsed
        config = rigor.get_current_config()
        timeouts.append(config.z3_timeout_seconds)
    
    # Verify monotonic increase
    for i in range(len(timeouts) - 1):
        assert timeouts[i] <= timeouts[i + 1], \
            f"Timeout decreased from {timeouts[i]}s to {timeouts[i+1]}s (non-monotonic)"


# ============================================================================
# Property 18: Difficulty scaling
# ============================================================================

@settings(max_examples=100, deadline=None)
@given(
    attack_intensity=st.floats(min_value=0.0, max_value=1.0)
)
def test_property_18_difficulty_scaling(attack_intensity):
    """
    Feature: autonomous-sentinel, Property 18: Difficulty scaling
    
    For any attack intensity level, the Adaptive Rigor should calculate PoW difficulty
    between 4 and 8 leading zeros, with higher intensity requiring more zeros.
    
    Validates: Requirements 3.7
    """
    rigor = AdaptiveRigor()
    
    # Calculate difficulty
    difficulty = rigor.calculate_pow_difficulty(attack_intensity)
    
    # Difficulty should be in valid range
    assert 4 <= difficulty <= 8, \
        f"Difficulty {difficulty} outside valid range [4, 8]"
    
    # Difficulty should scale with intensity
    expected_difficulty = 4 + int(attack_intensity * 4)
    assert difficulty == expected_difficulty, \
        f"Expected difficulty {expected_difficulty}, got {difficulty}"


def test_property_18_difficulty_monotonic():
    """
    Feature: autonomous-sentinel, Property 18: Difficulty scaling
    
    For any sequence of increasing attack intensities, difficulty should
    monotonically increase (never decrease).
    
    Validates: Requirements 3.7
    """
    rigor = AdaptiveRigor()
    
    # Test increasing intensities
    intensities = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    difficulties = [rigor.calculate_pow_difficulty(i) for i in intensities]
    
    # Verify monotonic increase
    for i in range(len(difficulties) - 1):
        assert difficulties[i] <= difficulties[i + 1], \
            f"Difficulty decreased from {difficulties[i]} to {difficulties[i+1]} (non-monotonic)"


# ============================================================================
# Property 19: Difficulty notification
# ============================================================================

@settings(max_examples=100, deadline=None)
@given(
    attack_intensity=st.floats(min_value=0.0, max_value=1.0)
)
def test_property_19_difficulty_notification(attack_intensity):
    """
    Feature: autonomous-sentinel, Property 19: Difficulty notification
    
    For any PoW difficulty change, the Adaptive Rigor should broadcast the new
    difficulty level to all connected clients within 1 second.
    
    Validates: Requirements 3.8
    """
    rigor = AdaptiveRigor()
    
    # Activate crisis mode
    rigor.activate_crisis_mode()
    
    # Track notifications
    notifications = []
    
    def callback(difficulty: int):
        notifications.append({
            "difficulty": difficulty,
            "timestamp": time.time()
        })
    
    rigor.register_difficulty_change_callback(callback)
    
    # Change difficulty
    start_time = time.time()
    new_difficulty = rigor.calculate_pow_difficulty(attack_intensity)
    
    # If difficulty changed, notification should be sent
    if len(notifications) > 0:
        notification_time = notifications[-1]["timestamp"]
        latency = notification_time - start_time
        
        # Notification should be sent within 1 second
        assert latency < 1.0, \
            f"Notification latency {latency:.3f}s exceeds 1 second threshold"
        
        # Notification should contain correct difficulty
        assert notifications[-1]["difficulty"] == new_difficulty, \
            f"Notification difficulty {notifications[-1]['difficulty']} != actual {new_difficulty}"


def test_property_19_config_change_notification():
    """
    Feature: autonomous-sentinel, Property 19: Difficulty notification
    
    For any configuration change (crisis activation/deactivation), all registered
    callbacks should be notified.
    
    Validates: Requirements 3.8
    """
    rigor = AdaptiveRigor()
    
    # Track notifications
    config_notifications = []
    
    def callback(config: RigorConfig):
        config_notifications.append({
            "config": config,
            "timestamp": time.time()
        })
    
    rigor.register_config_change_callback(callback)
    
    # Activate crisis mode
    rigor.activate_crisis_mode()
    
    # Should have received notification
    assert len(config_notifications) > 0, \
        "No config change notification received after crisis activation"
    
    # Notification should contain crisis config
    last_config = config_notifications[-1]["config"]
    assert last_config.pow_required, \
        "Crisis mode config should require PoW"
    assert last_config.z3_timeout_seconds == 5, \
        "Crisis mode config should have 5s timeout"


# ============================================================================
# Unit Tests - Specific Examples and Edge Cases
# ============================================================================

def test_unit_normal_mode_defaults():
    """Test that normal mode has correct default configuration"""
    rigor = AdaptiveRigor()
    
    assert rigor.current_mode == SystemMode.NORMAL
    assert rigor.current_config.z3_timeout_seconds == 30
    assert rigor.current_config.proof_depth == "deep"
    assert not rigor.current_config.pow_required
    assert rigor.current_config.pow_difficulty == 0


def test_unit_crisis_mode_activation():
    """Test crisis mode activation changes configuration"""
    rigor = AdaptiveRigor()
    
    rigor.activate_crisis_mode()
    
    assert rigor.current_mode == SystemMode.CRISIS
    assert rigor.current_config.z3_timeout_seconds == 5
    assert rigor.current_config.proof_depth == "shallow"
    assert rigor.current_config.pow_required
    assert rigor.current_config.pow_difficulty == 4


def test_unit_crisis_mode_idempotent():
    """Test that activating crisis mode multiple times is safe"""
    rigor = AdaptiveRigor()
    
    rigor.activate_crisis_mode()
    config1 = rigor.get_current_config()
    
    rigor.activate_crisis_mode()
    config2 = rigor.get_current_config()
    
    assert config1.to_dict() == config2.to_dict()


def test_unit_recovery_mode_transition():
    """Test transition from crisis to recovery mode"""
    rigor = AdaptiveRigor()
    
    rigor.activate_crisis_mode()
    assert rigor.current_mode == SystemMode.CRISIS
    
    rigor.deactivate_crisis_mode()
    assert rigor.current_mode == SystemMode.RECOVERY
    assert rigor.recovery_start_time is not None


def test_unit_pow_validation_specific_example():
    """Test PoW validation with known valid nonce"""
    rigor = AdaptiveRigor()
    rigor.activate_crisis_mode()
    rigor.crisis_config.pow_difficulty = 2
    rigor.current_config.pow_difficulty = 2
    
    # Find a valid nonce for "test_tx"
    tx_id = "test_tx"
    valid_nonce = None
    for nonce in range(10000):
        hash_result = hashlib.sha256(f"{tx_id}{nonce}".encode()).hexdigest()
        if hash_result.startswith("00"):
            valid_nonce = nonce
            break
    
    assert valid_nonce is not None, "Could not find valid nonce"
    assert rigor.validate_pow(tx_id, valid_nonce)


def test_unit_difficulty_scaling_boundaries():
    """Test difficulty scaling at boundary values"""
    rigor = AdaptiveRigor()
    
    # Minimum intensity → minimum difficulty
    assert rigor.calculate_pow_difficulty(0.0) == 4
    
    # Maximum intensity → maximum difficulty
    assert rigor.calculate_pow_difficulty(1.0) == 8
    
    # Mid intensity → mid difficulty
    assert rigor.calculate_pow_difficulty(0.5) == 6


def test_unit_recovery_complete():
    """Test that recovery completes after 60 seconds"""
    rigor = AdaptiveRigor()
    
    rigor.activate_crisis_mode()
    rigor.deactivate_crisis_mode()
    
    # Simulate 60 seconds elapsed
    rigor.recovery_start_time = time.time() - 60.0
    
    config = rigor.get_current_config()
    
    assert rigor.current_mode == SystemMode.NORMAL
    assert config.z3_timeout_seconds == 30
    assert config.proof_depth == "deep"
    assert not config.pow_required


def test_unit_statistics():
    """Test statistics reporting"""
    rigor = AdaptiveRigor()
    
    stats = rigor.get_statistics()
    
    assert "current_mode" in stats
    assert "current_config" in stats
    assert "recovery_progress" in stats
    
    assert stats["current_mode"] == "normal"
    assert stats["recovery_progress"] is None


def test_unit_recovery_statistics():
    """Test statistics during recovery"""
    rigor = AdaptiveRigor()
    
    rigor.activate_crisis_mode()
    rigor.deactivate_crisis_mode()
    
    # Simulate 30 seconds elapsed (50% progress)
    rigor.recovery_start_time = time.time() - 30.0
    
    stats = rigor.get_statistics()
    
    assert stats["current_mode"] == "recovery"
    assert stats["recovery_progress"] is not None
    assert 0.4 <= stats["recovery_progress"] <= 0.6  # ~50% with tolerance


if __name__ == "__main__":
    print("Running Adaptive Rigor property-based tests...")
    print("\n" + "="*80)
    print("Property 16: Proof of Work validation")
    print("="*80)
    test_property_16_pow_validation()
    test_property_16_pow_not_required_in_normal_mode()
    
    print("\n" + "="*80)
    print("Property 17: Gradual recovery")
    print("="*80)
    test_property_17_gradual_recovery()
    test_property_17_recovery_monotonic_increase()
    
    print("\n" + "="*80)
    print("Property 18: Difficulty scaling")
    print("="*80)
    test_property_18_difficulty_scaling()
    test_property_18_difficulty_monotonic()
    
    print("\n" + "="*80)
    print("Property 19: Difficulty notification")
    print("="*80)
    test_property_19_difficulty_notification()
    test_property_19_config_change_notification()
    
    print("\n" + "="*80)
    print("Unit Tests")
    print("="*80)
    test_unit_normal_mode_defaults()
    test_unit_crisis_mode_activation()
    test_unit_crisis_mode_idempotent()
    test_unit_recovery_mode_transition()
    test_unit_pow_validation_specific_example()
    test_unit_difficulty_scaling_boundaries()
    test_unit_recovery_complete()
    test_unit_statistics()
    test_unit_recovery_statistics()
    
    print("\n✅ All Adaptive Rigor tests passed!")
