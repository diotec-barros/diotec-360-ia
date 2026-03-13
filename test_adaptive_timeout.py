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
Property-based tests for adaptive timeout adjustment.

This module tests the adaptive timeout system for the Proof-of-Proof consensus
protocol. It validates that timeouts are dynamically adjusted based on network
latency and that exponential backoff is applied for view changes.
"""

import pytest
from hypothesis import given, settings, strategies as st
import time

from diotec360.consensus.network_monitor import NetworkMonitor, LatencyMeasurement
from diotec360.consensus.adaptive_timeout import AdaptiveTimeoutManager


# ============================================================================
# Property 26: Adaptive Timeout Adjustment
# ============================================================================

@settings(max_examples=10, deadline=5000)
@given(
    latency=st.floats(min_value=100.0, max_value=2000.0),
)
def test_property_26_adaptive_timeout_adjustment(latency):
    """
    Feature: proof-of-proof-consensus
    Property 26: Adaptive Timeout Adjustment
    
    For any network condition where latency exceeds 500ms, the system must
    dynamically increase consensus timeouts to prevent premature view changes.
    
    Validates: Requirements 6.5
    """
    # Create adaptive timeout manager
    timeout_manager = AdaptiveTimeoutManager(
        base_timeout=10.0,
        min_timeout=5.0,
        max_timeout=120.0,
        latency_threshold=500.0,
    )
    
    # Get initial timeout
    initial_timeout = timeout_manager.get_consensus_timeout()
    
    # Adjust for latency
    adjusted_timeout = timeout_manager.adjust_for_latency(latency)
    
    # Verify timeout adjustment based on latency
    if latency > 500.0:
        # High latency - timeout should increase
        assert adjusted_timeout > initial_timeout, \
            f"Timeout should increase for high latency ({latency}ms)"
        
        # Verify timeout is bounded
        assert adjusted_timeout <= timeout_manager.max_timeout
        assert adjusted_timeout >= timeout_manager.min_timeout
        
    else:
        # Normal latency - timeout should be base timeout
        assert abs(adjusted_timeout - timeout_manager.base_timeout) < 0.1, \
            f"Timeout should be base for normal latency ({latency}ms)"


def test_exponential_backoff_for_view_changes():
    """
    Test exponential backoff for view changes.
    
    Verifies that each view change increases the timeout exponentially.
    """
    timeout_manager = AdaptiveTimeoutManager(
        base_timeout=10.0,
        backoff_multiplier=1.5,
    )
    
    # Initial timeout
    timeout_0 = timeout_manager.get_view_change_timeout()
    
    # First view change
    timeout_1 = timeout_manager.apply_view_change_backoff()
    assert timeout_1 > timeout_0
    
    # Second view change
    timeout_2 = timeout_manager.apply_view_change_backoff()
    assert timeout_2 > timeout_1
    
    # Third view change
    timeout_3 = timeout_manager.apply_view_change_backoff()
    assert timeout_3 > timeout_2
    
    # Verify exponential growth
    ratio_1_2 = timeout_2 / timeout_1
    ratio_2_3 = timeout_3 / timeout_2
    
    # Ratios should be approximately equal (exponential)
    assert abs(ratio_1_2 - ratio_2_3) < 0.5


def test_timeout_reset_after_successful_consensus():
    """
    Test that view change backoff is reset after successful consensus.
    """
    timeout_manager = AdaptiveTimeoutManager(base_timeout=10.0)
    
    # Apply several view changes
    timeout_manager.apply_view_change_backoff()
    timeout_manager.apply_view_change_backoff()
    timeout_manager.apply_view_change_backoff()
    
    assert timeout_manager.config.view_change_count == 3
    
    # Reset after successful consensus
    timeout_manager.reset_view_change_backoff()
    
    assert timeout_manager.config.view_change_count == 0
    
    # Next timeout should be back to base
    timeout = timeout_manager.get_view_change_timeout()
    assert abs(timeout - timeout_manager.base_timeout) < 0.1


def test_timeout_bounds_enforcement():
    """
    Test that timeouts are always within configured bounds.
    """
    timeout_manager = AdaptiveTimeoutManager(
        base_timeout=10.0,
        min_timeout=5.0,
        max_timeout=30.0,
    )
    
    # Test with very high latency
    timeout = timeout_manager.adjust_for_latency(5000.0)
    assert timeout <= 30.0  # Should not exceed max
    assert timeout >= 5.0   # Should not go below min
    
    # Test with many view changes
    for _ in range(20):
        timeout = timeout_manager.apply_view_change_backoff()
        assert timeout <= 30.0  # Should not exceed max


def test_network_monitor_latency_measurement():
    """
    Test network monitor latency measurement.
    """
    monitor = NetworkMonitor(window_size=50)
    
    # Record some latency measurements
    monitor.record_latency("peer_1", 100.0, success=True)
    monitor.record_latency("peer_1", 150.0, success=True)
    monitor.record_latency("peer_1", 200.0, success=True)
    
    # Get peer statistics
    stats = monitor.get_peer_latency("peer_1")
    
    assert stats is not None
    assert stats.peer_id == "peer_1"
    assert stats.measurement_count == 3
    assert stats.average_latency == 150.0
    assert stats.min_latency == 100.0
    assert stats.max_latency == 200.0


def test_network_monitor_average_latency():
    """
    Test average network latency calculation across multiple peers.
    """
    monitor = NetworkMonitor()
    
    # Record measurements for multiple peers
    monitor.record_latency("peer_1", 100.0, success=True)
    monitor.record_latency("peer_1", 200.0, success=True)
    monitor.record_latency("peer_2", 300.0, success=True)
    monitor.record_latency("peer_2", 400.0, success=True)
    
    # Average should be (100 + 200 + 300 + 400) / 4 = 250
    avg_latency = monitor.get_average_network_latency()
    assert abs(avg_latency - 250.0) < 0.1


def test_high_latency_detection():
    """
    Test detection of high latency conditions.
    """
    monitor = NetworkMonitor()
    
    # Record normal latency
    monitor.record_latency("peer_1", 100.0, success=True)
    assert not monitor.is_high_latency(threshold=500.0)
    
    # Record more high latency measurements to push average above threshold
    monitor.record_latency("peer_1", 600.0, success=True)
    monitor.record_latency("peer_1", 700.0, success=True)
    monitor.record_latency("peer_1", 650.0, success=True)
    
    # Average is now (100+600+700+650)/4 = 512.5, should detect high latency
    assert monitor.is_high_latency(threshold=500.0)


def test_integration_monitor_and_timeout_manager():
    """
    Integration test: Network monitor with adaptive timeout manager.
    
    Verifies that the two components work together correctly.
    """
    monitor = NetworkMonitor()
    timeout_manager = AdaptiveTimeoutManager(base_timeout=10.0)
    
    # Simulate normal latency
    monitor.record_latency("peer_1", 100.0, success=True)
    monitor.record_latency("peer_2", 150.0, success=True)
    
    avg_latency = monitor.get_average_network_latency()
    timeout = timeout_manager.get_consensus_timeout(avg_latency)
    
    # Should use base timeout for normal latency
    assert abs(timeout - 10.0) < 0.1
    
    # Simulate sustained high latency - record enough measurements to push average above 500ms
    monitor.record_latency("peer_1", 600.0, success=True)
    monitor.record_latency("peer_2", 700.0, success=True)
    monitor.record_latency("peer_1", 650.0, success=True)
    monitor.record_latency("peer_2", 750.0, success=True)
    
    # Average is now (100+150+600+700+650+750)/6 = 491.67, still below 500
    # Add one more to push it over
    monitor.record_latency("peer_1", 800.0, success=True)
    
    # Average is now (100+150+600+700+650+750+800)/7 = 535.71, above 500
    avg_latency = monitor.get_average_network_latency()
    timeout = timeout_manager.get_consensus_timeout(avg_latency)
    
    # Should increase timeout for high latency
    assert timeout > 10.0


def test_timeout_phases():
    """
    Test different timeout phases (PREPARE, COMMIT, VIEW_CHANGE).
    """
    timeout_manager = AdaptiveTimeoutManager(base_timeout=10.0)
    
    # Get timeouts for different phases
    consensus_timeout = timeout_manager.get_consensus_timeout()
    prepare_timeout = timeout_manager.get_prepare_timeout()
    commit_timeout = timeout_manager.get_commit_timeout()
    
    # PREPARE and COMMIT should be fractions of consensus timeout
    assert prepare_timeout < consensus_timeout
    assert commit_timeout < consensus_timeout
    
    # Apply view change
    view_change_timeout = timeout_manager.apply_view_change_backoff()
    
    # View change timeout should be higher due to backoff
    assert view_change_timeout >= consensus_timeout


def test_timeout_adjustment_history():
    """
    Test that timeout adjustments are recorded in history.
    """
    timeout_manager = AdaptiveTimeoutManager(base_timeout=10.0)
    
    # Make several adjustments
    timeout_manager.adjust_for_latency(600.0)
    timeout_manager.apply_view_change_backoff()
    timeout_manager.adjust_for_latency(300.0)
    
    # Check history
    history = timeout_manager.get_adjustment_history()
    
    assert len(history) >= 2  # At least latency adjustment and view change
    
    # Verify history contains required fields
    for record in history:
        assert 'timestamp' in record
        assert 'reason' in record


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
