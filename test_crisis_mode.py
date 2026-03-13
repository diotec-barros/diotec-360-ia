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
Unit Tests for Crisis Mode Detection Logic
Testing the implementation of task 1.4 from the Autonomous Sentinel spec.

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.0 "The Autonomous Sentinel"
Date: February 4, 2026
"""

import pytest
import time
from diotec360.core.sentinel_monitor import SentinelMonitor, TransactionMetrics


def test_crisis_mode_activation_by_anomaly_rate():
    """
    Test that Crisis Mode activates when anomaly rate exceeds 10% in 60 seconds.
    
    Validates: Requirements 1.4, 8.1
    """
    monitor = SentinelMonitor(db_path=".test_crisis_anomaly.db")
    
    try:
        # Add 100 transactions, 15 of them anomalous (15% > 10% threshold)
        current_time = time.time()
        
        for i in range(100):
            # Make 15 transactions anomalous
            anomaly_score = 0.8 if i < 15 else 0.3
            
            metrics = TransactionMetrics(
                tx_id=f"tx_{i}",
                start_time=current_time - 30,  # Within 60-second window
                end_time=current_time - 29,
                cpu_time_ms=100.0,
                memory_delta_mb=10.0,
                z3_duration_ms=50.0,
                layer_results={"layer_0": True},
                anomaly_score=anomaly_score
            )
            monitor.metrics_window.append(metrics)
        
        # Check crisis conditions
        should_activate = monitor.check_crisis_conditions()
        
        assert should_activate, "Crisis Mode should activate with 15% anomaly rate"
        
    finally:
        import os
        if os.path.exists(".test_crisis_anomaly.db"):
            os.remove(".test_crisis_anomaly.db")


def test_crisis_mode_activation_by_request_rate():
    """
    Test that Crisis Mode activates when request rate exceeds 1000/second.
    
    Validates: Requirements 1.4, 8.2
    """
    monitor = SentinelMonitor(db_path=".test_crisis_requests.db")
    
    try:
        # Simulate 1000 requests in the last second (exactly at threshold)
        current_time = time.time()
        
        # Clear the deque first
        monitor.request_timestamps.clear()
        
        # Add 1000 timestamps within the last 0.5 seconds
        for i in range(1000):
            monitor.request_timestamps.append(current_time - 0.1)
        
        # Check crisis conditions - should activate with >= 1000 requests/second
        should_activate = monitor.check_crisis_conditions()
        
        assert should_activate, f"Crisis Mode should activate with 1000 requests/second"
        
    finally:
        import os
        if os.path.exists(".test_crisis_requests.db"):
            os.remove(".test_crisis_requests.db")


def test_crisis_mode_no_activation_normal_conditions():
    """
    Test that Crisis Mode does NOT activate under normal conditions.
    
    Validates: Requirements 1.4
    """
    monitor = SentinelMonitor(db_path=".test_crisis_normal.db")
    
    try:
        # Add 100 normal transactions (5% anomaly rate, well below 10%)
        current_time = time.time()
        
        for i in range(100):
            # Make only 5 transactions anomalous (5% < 10% threshold)
            anomaly_score = 0.8 if i < 5 else 0.3
            
            metrics = TransactionMetrics(
                tx_id=f"tx_{i}",
                start_time=current_time - 30,
                end_time=current_time - 29,
                cpu_time_ms=100.0,
                memory_delta_mb=10.0,
                z3_duration_ms=50.0,
                layer_results={"layer_0": True},
                anomaly_score=anomaly_score
            )
            monitor.metrics_window.append(metrics)
        
        # Simulate normal request rate (500 requests/second)
        for i in range(500):
            monitor.request_timestamps.append(current_time - 0.5)
        
        # Check crisis conditions
        should_activate = monitor.check_crisis_conditions()
        
        assert not should_activate, "Crisis Mode should NOT activate under normal conditions"
        
    finally:
        import os
        if os.path.exists(".test_crisis_normal.db"):
            os.remove(".test_crisis_normal.db")


def test_crisis_mode_state_broadcasting():
    """
    Test that Crisis Mode state changes are broadcast to listeners.
    
    Validates: Requirements 8.3, 8.6
    """
    monitor = SentinelMonitor(db_path=".test_crisis_broadcast.db")
    
    try:
        # Track listener calls
        listener_calls = []
        
        def test_listener(active: bool):
            listener_calls.append(active)
        
        monitor.register_crisis_listener(test_listener)
        
        # Trigger Crisis Mode activation
        current_time = time.time()
        for i in range(100):
            anomaly_score = 0.8 if i < 15 else 0.3
            metrics = TransactionMetrics(
                tx_id=f"tx_{i}",
                start_time=current_time - 30,
                end_time=current_time - 29,
                cpu_time_ms=100.0,
                memory_delta_mb=10.0,
                z3_duration_ms=50.0,
                layer_results={"layer_0": True},
                anomaly_score=anomaly_score
            )
            monitor.metrics_window.append(metrics)
        
        # Manually activate (simulating what end_transaction would do)
        if monitor.check_crisis_conditions():
            monitor._activate_crisis_mode()
        
        # Verify listener was called with active=True
        assert len(listener_calls) > 0, "Listener should be called"
        assert listener_calls[-1] == True, "Listener should receive active=True"
        
    finally:
        import os
        if os.path.exists(".test_crisis_broadcast.db"):
            os.remove(".test_crisis_broadcast.db")


def test_crisis_mode_deactivation_cooldown():
    """
    Test that Crisis Mode requires 120 seconds of low anomaly rate before deactivating.
    
    Validates: Requirements 8.5
    """
    monitor = SentinelMonitor(db_path=".test_crisis_cooldown.db")
    
    try:
        # Activate Crisis Mode
        monitor.crisis_mode_active = True
        monitor.crisis_mode_activated_at = time.time()
        
        # Add metrics with low anomaly rate (1% < 2% threshold)
        current_time = time.time()
        for i in range(100):
            anomaly_score = 0.8 if i < 1 else 0.3  # Only 1% anomalous
            metrics = TransactionMetrics(
                tx_id=f"tx_{i}",
                start_time=current_time - 60,  # Within 120-second window
                end_time=current_time - 59,
                cpu_time_ms=100.0,
                memory_delta_mb=10.0,
                z3_duration_ms=50.0,
                layer_results={"layer_0": True},
                anomaly_score=anomaly_score
            )
            monitor.metrics_window.append(metrics)
        
        # First call should set deactivation candidate time
        monitor._deactivate_crisis_mode()
        assert monitor.crisis_mode_active, "Crisis Mode should still be active (cooldown not complete)"
        assert monitor.crisis_mode_deactivation_candidate_at is not None, "Deactivation tracking should start"
        
        # Simulate 120 seconds passing by setting the candidate time to 121 seconds ago
        monitor.crisis_mode_deactivation_candidate_at = current_time - 121
        
        # Now deactivation should succeed
        monitor._deactivate_crisis_mode()
        assert not monitor.crisis_mode_active, "Crisis Mode should deactivate after 120-second cooldown"
        
    finally:
        import os
        if os.path.exists(".test_crisis_cooldown.db"):
            os.remove(".test_crisis_cooldown.db")


def test_crisis_mode_transition_logging():
    """
    Test that Crisis Mode transitions are logged to the database.
    
    Validates: Requirements 8.7
    """
    import sqlite3
    
    monitor = SentinelMonitor(db_path=".test_crisis_logging.db")
    
    try:
        # Activate Crisis Mode
        current_time = time.time()
        for i in range(100):
            anomaly_score = 0.8 if i < 15 else 0.3
            metrics = TransactionMetrics(
                tx_id=f"tx_{i}",
                start_time=current_time - 30,
                end_time=current_time - 29,
                cpu_time_ms=100.0,
                memory_delta_mb=10.0,
                z3_duration_ms=50.0,
                layer_results={"layer_0": True},
                anomaly_score=anomaly_score
            )
            monitor.metrics_window.append(metrics)
        
        if monitor.check_crisis_conditions():
            monitor._activate_crisis_mode()
        
        # Check database for transition log
        conn = sqlite3.connect(".test_crisis_logging.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT transition_type, anomaly_rate, triggering_condition 
            FROM crisis_mode_transitions 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None, "Transition should be logged to database"
        assert row[0] == "activation", "Transition type should be 'activation'"
        assert row[1] >= 0.10, "Anomaly rate should be >= 10%"
        assert "threshold" in row[2].lower(), "Triggering condition should mention threshold"
        
    finally:
        import os
        if os.path.exists(".test_crisis_logging.db"):
            os.remove(".test_crisis_logging.db")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
