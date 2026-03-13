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
Test for Sentinel Monitor SQLite Persistence (Task 1.8)

Validates that metrics are persisted to SQLite database asynchronously
without blocking the main thread.

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.0 "The Autonomous Sentinel"
Date: February 4, 2026
"""

import pytest
import time
import sqlite3
from pathlib import Path
from diotec360.core.sentinel_monitor import SentinelMonitor


def test_async_persistence():
    """
    Test that metrics are persisted to database asynchronously.
    
    Validates Requirements 1.1, 1.2 from autonomous-sentinel spec.
    """
    db_path = ".test_sentinel_persistence.db"
    monitor = SentinelMonitor(db_path=db_path)
    
    try:
        # Start and end multiple transactions
        for i in range(10):
            tx_id = f"tx_{i}"
            monitor.start_transaction(tx_id)
            time.sleep(0.01)  # Minimal work
            monitor.end_transaction(tx_id, {"layer_0": True, "layer_1": True})
        
        # Give async writes time to complete
        monitor.shutdown()
        time.sleep(0.5)
        
        # Verify data was persisted
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM transaction_metrics")
        count = cursor.fetchone()[0]
        
        assert count == 10, f"Expected 10 persisted metrics, got {count}"
        
        # Verify structure
        cursor.execute("SELECT * FROM transaction_metrics LIMIT 1")
        row = cursor.fetchone()
        assert row is not None, "Should have at least one row"
        
        # Verify columns
        cursor.execute("PRAGMA table_info(transaction_metrics)")
        columns = [col[1] for col in cursor.fetchall()]
        
        expected_columns = [
            'tx_id', 'timestamp', 'cpu_time_ms', 'memory_delta_mb',
            'z3_duration_ms', 'anomaly_score', 'layer_results', 'outcome'
        ]
        
        for col in expected_columns:
            assert col in columns, f"Missing column: {col}"
        
        conn.close()
        
        print("[TEST] ✅ Async persistence validated")
        
    finally:
        # Cleanup - wait for file handles to be released
        time.sleep(1.0)
        import os
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except PermissionError:
            # File still locked on Windows, ignore
            pass


def test_persistence_non_blocking():
    """
    Test that database writes don't block transaction processing.
    
    Validates that async persistence improves throughput.
    """
    db_path = ".test_sentinel_nonblocking.db"
    monitor = SentinelMonitor(db_path=db_path)
    
    try:
        start_time = time.time()
        
        # Process 50 transactions rapidly
        for i in range(50):
            tx_id = f"tx_{i}"
            monitor.start_transaction(tx_id)
            monitor.end_transaction(tx_id, {"layer_0": True})
        
        elapsed = time.time() - start_time
        
        # Should complete quickly (< 1 second) because writes are async
        assert elapsed < 1.0, f"Processing took {elapsed:.2f}s, should be < 1s with async writes"
        
        # Shutdown and wait for writes
        monitor.shutdown()
        time.sleep(1.5)  # Increased wait time for all writes to complete
        
        # Verify all were persisted
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transaction_metrics")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 50, f"Expected 50 persisted metrics, got {count}"
        
        print(f"[TEST] ✅ Non-blocking persistence validated ({elapsed:.3f}s for 50 transactions)")
        
    finally:
        # Cleanup - wait for file handles to be released
        time.sleep(1.0)
        import os
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
        except PermissionError:
            # File still locked on Windows, ignore
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
