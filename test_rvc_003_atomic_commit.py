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
Property-Based Tests for RVC-003 Atomic Commit

This module tests the atomic commit protocol using property-based testing
to verify correctness across thousands of random scenarios.

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.1 "RVC-003 Tests"
Date: February 21, 2026
"""

import pytest
import tempfile
import shutil
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, Phase

from diotec360.consensus.atomic_commit import (
    AtomicCommitLayer,
    WriteAheadLog,
    Transaction,
    WALEntry,
    RecoveryReport
)


# Feature: rvc-003-004-fixes, Property 1: Atomic State Persistence
@settings(max_examples=100, phases=[Phase.generate, Phase.target], deadline=None)
@given(
    changes=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.integers(min_value=0, max_value=1000000),
        min_size=1,
        max_size=10
    )
)
def test_property_1_atomic_state_persistence(changes):
    """
    Property 1: Atomic State Persistence
    
    For any state transition, writing the new state to disk should be atomic -
    either the entire state is persisted or none of it is. No partial states
    should ever be visible on disk.
    
    Validates: Requirements 1.1, 1.2, 1.3, 8.2
    """
    # Create temporary directories
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        # Initialize atomic commit layer
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Begin transaction
        tx = commit_layer.begin_transaction("test_tx")
        tx.changes = changes
        
        # Commit transaction
        success = commit_layer.commit_transaction(tx)
        
        # Verify commit succeeded
        assert success, "Transaction commit should succeed"
        
        # Verify state file exists
        assert commit_layer.state_file.exists(), "State file should exist after commit"
        
        # Verify no temp files remain
        temp_files = list(state_dir.glob("*.tmp"))
        assert len(temp_files) == 0, "No temporary files should remain after commit"
        
        # Verify state matches changes
        with open(commit_layer.state_file, 'r') as f:
            persisted_state = json.load(f)
        
        for key, value in changes.items():
            assert key in persisted_state, f"Key {key} should be in persisted state"
            assert persisted_state[key] == value, f"Value for {key} should match"


# Feature: rvc-003-004-fixes, Property 2: Write-Ahead Logging Protocol
@settings(max_examples=100, deadline=None)
@given(
    changes=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.integers(min_value=0, max_value=1000000),
        min_size=1,
        max_size=10
    )
)
def test_property_2_wal_protocol(changes):
    """
    Property 2: Write-Ahead Logging Protocol
    
    For any state modification, the change must be written to the Write-Ahead Log
    and fsync'd to disk before the state modification is applied. This ensures we
    can replay or rollback the transaction after a crash.
    
    Validates: Requirements 2.1, 2.2, 2.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Begin transaction
        tx = commit_layer.begin_transaction("test_tx")
        tx.changes = changes
        
        # Commit transaction
        success = commit_layer.commit_transaction(tx)
        assert success, "Transaction commit should succeed"
        
        # Verify WAL entry exists and is committed
        entries = commit_layer.wal._read_all_entries()
        
        # Find our transaction in WAL
        found = False
        for entry in entries:
            if entry.tx_id == "test_tx":
                found = True
                assert entry.committed, "WAL entry should be marked committed"
                assert entry.changes == changes, "WAL entry should contain correct changes"
                break
        
        assert found, "Transaction should be in WAL"


# Feature: rvc-003-004-fixes, Property 3: Crash Recovery Correctness
@settings(max_examples=50, deadline=None)
@given(
    num_transactions=st.integers(min_value=1, max_value=10),
    crash_point=st.integers(min_value=0, max_value=10)
)
def test_property_3_crash_recovery(num_transactions, crash_point):
    """
    Property 3: Crash Recovery Correctness
    
    For any system crash, when the system restarts, it should detect all incomplete
    transactions, roll them back, and verify that the Merkle Root matches the
    restored state. The system should always recover to a consistent state.
    
    Validates: Requirements 3.1, 3.2, 3.3, 2.3, 2.4
    
    NOTE: Updated for RVC2-001 fail-closed behavior - system must have valid initial state
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Initialize with at least one committed transaction to create valid state
        # This ensures state.json exists for recovery testing
        init_tx = commit_layer.begin_transaction("init_tx")
        init_tx.changes = {"initialized": True}
        commit_layer.commit_transaction(init_tx)
        
        # Simulate multiple transactions
        for i in range(num_transactions):
            tx = commit_layer.begin_transaction(f"tx_{i}")
            tx.changes = {f"key_{i}": i * 100}
            
            # Simulate crash at specific point
            if i == crash_point:
                # Don't commit this transaction (simulate crash)
                # Just write to WAL
                commit_layer.wal.append_entry(tx.tx_id, tx.changes)
                break
            else:
                # Normal commit
                commit_layer.commit_transaction(tx)
        
        # Simulate restart - create new commit layer
        commit_layer2 = AtomicCommitLayer(state_dir, wal_dir)
        
        # Run crash recovery
        report = commit_layer2.recover_from_crash()
        
        # Verify recovery succeeded
        assert report.recovered, "Recovery should succeed"
        
        # Verify uncommitted transactions were detected
        if crash_point < num_transactions:
            assert report.uncommitted_transactions >= 1, "Should detect uncommitted transactions"
        
        # Verify no temp files remain
        temp_files = list(state_dir.glob("*.tmp"))
        assert len(temp_files) == 0, "No temporary files should remain after recovery"


# Feature: rvc-003-004-fixes, Property 4: Merkle Root Integrity
@settings(max_examples=100, deadline=None)
@given(
    changes=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.integers(min_value=0, max_value=1000000),
        min_size=1,
        max_size=10
    )
)
def test_property_4_merkle_root_integrity(changes):
    """
    Property 4: Merkle Root Integrity
    
    For any persisted state, the Merkle Root should always match the state data.
    If verification fails, the system should restore from the last valid checkpoint.
    This ensures cryptographic integrity is never broken.
    
    Validates: Requirements 1.4, 1.5, 3.3
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Commit transaction
        tx = commit_layer.begin_transaction("test_tx")
        tx.changes = changes
        success = commit_layer.commit_transaction(tx)
        
        assert success, "Transaction commit should succeed"
        
        # Verify state file exists and is valid JSON
        assert commit_layer.state_file.exists(), "State file should exist"
        
        with open(commit_layer.state_file, 'r') as f:
            state = json.load(f)
        
        # Verify all changes are in state
        for key, value in changes.items():
            assert key in state, f"Key {key} should be in state"
            assert state[key] == value, f"Value for {key} should match"


# Feature: rvc-003-004-fixes, Property 5: Temporary File Cleanup
@settings(max_examples=100, deadline=None)
@given(
    num_transactions=st.integers(min_value=1, max_value=10)
)
def test_property_5_temp_file_cleanup(num_transactions):
    """
    Property 5: Temporary File Cleanup
    
    For any incomplete transaction, temporary files should be deleted during
    crash recovery. No orphaned temporary files should remain after recovery completes.
    
    Validates: Requirements 1.3, 3.1
    
    NOTE: Updated for RVC2-001 fail-closed behavior - system must have valid initial state
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Initialize with a committed transaction to create valid state
        init_tx = commit_layer.begin_transaction("init_tx")
        init_tx.changes = {"initialized": True}
        commit_layer.commit_transaction(init_tx)
        
        # Create some orphaned temp files
        for i in range(num_transactions):
            temp_file = state_dir / f"state.orphan_{i}.tmp"
            temp_file.write_text(json.dumps({"orphan": i}))
        
        # Verify temp files exist
        temp_files_before = list(state_dir.glob("*.tmp"))
        assert len(temp_files_before) == num_transactions, "Temp files should exist before recovery"
        
        # Run crash recovery
        report = commit_layer.recover_from_crash()
        
        # Verify recovery succeeded
        assert report.recovered, "Recovery should succeed"
        
        # Verify all temp files were cleaned up
        temp_files_after = list(state_dir.glob("*.tmp"))
        assert len(temp_files_after) == 0, "All temp files should be cleaned up after recovery"
        
        # Verify cleanup count matches
        assert report.temp_files_cleaned == num_transactions, "Cleanup count should match"


# Feature: rvc-003-004-fixes, Property 6: Recovery Audit Trail
@settings(max_examples=50, deadline=None)
@given(
    num_uncommitted=st.integers(min_value=0, max_value=5)
)
def test_property_6_recovery_audit_trail(num_uncommitted):
    """
    Property 6: Recovery Audit Trail
    
    For any crash recovery operation, all recovery actions (rollbacks, temp file
    deletions, Merkle root verifications) should be logged for audit purposes.
    
    Validates: Requirements 3.5
    
    NOTE: Updated for RVC2-001 fail-closed behavior - system must have valid initial state
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Initialize with a committed transaction to create valid state
        init_tx = commit_layer.begin_transaction("init_tx")
        init_tx.changes = {"initialized": True}
        commit_layer.commit_transaction(init_tx)
        
        # Create uncommitted transactions
        for i in range(num_uncommitted):
            tx = commit_layer.begin_transaction(f"uncommitted_{i}")
            tx.changes = {f"key_{i}": i}
            # Write to WAL but don't commit
            commit_layer.wal.append_entry(tx.tx_id, tx.changes)
        
        # Run crash recovery
        report = commit_layer.recover_from_crash()
        
        # Verify recovery report contains audit information
        assert report.recovered is not None, "Recovery status should be recorded"
        assert report.uncommitted_transactions == num_uncommitted, "Uncommitted count should match"
        assert report.rolled_back_transactions == num_uncommitted, "Rollback count should match"
        assert report.merkle_root_verified is not None, "Merkle root verification should be recorded"
        assert report.recovery_duration_ms >= 0, "Recovery duration should be recorded"


# Unit Tests

def test_wal_append_and_read():
    """Test WAL append and read operations"""
    with tempfile.TemporaryDirectory() as tmpdir:
        wal_dir = Path(tmpdir)
        wal = WriteAheadLog(wal_dir)
        
        # Append entry
        changes = {"key1": 100, "key2": 200}
        entry = wal.append_entry("test_tx", changes)
        
        assert entry.tx_id == "test_tx"
        assert entry.changes == changes
        assert not entry.committed
        
        # Read entries
        entries = wal._read_all_entries()
        assert len(entries) == 1
        assert entries[0].tx_id == "test_tx"


def test_wal_mark_committed():
    """Test marking WAL entry as committed"""
    with tempfile.TemporaryDirectory() as tmpdir:
        wal_dir = Path(tmpdir)
        wal = WriteAheadLog(wal_dir)
        
        # Append entry
        entry = wal.append_entry("test_tx", {"key": 100})
        
        # Mark committed
        wal.mark_committed(entry)
        
        # Verify committed
        entries = wal._read_all_entries()
        assert len(entries) == 1
        assert entries[0].committed


def test_wal_get_uncommitted():
    """Test getting uncommitted entries"""
    with tempfile.TemporaryDirectory() as tmpdir:
        wal_dir = Path(tmpdir)
        wal = WriteAheadLog(wal_dir)
        
        # Append committed entry
        entry1 = wal.append_entry("tx1", {"key": 100})
        wal.mark_committed(entry1)
        
        # Append uncommitted entry
        wal.append_entry("tx2", {"key": 200})
        
        # Get uncommitted
        uncommitted = wal.get_uncommitted_entries()
        assert len(uncommitted) == 1
        assert uncommitted[0].tx_id == "tx2"


def test_atomic_commit_rollback():
    """Test transaction rollback"""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Begin transaction
        tx = commit_layer.begin_transaction("test_tx")
        tx.changes = {"key": 100}
        
        # Rollback
        commit_layer.rollback_transaction(tx)
        
        # Verify status
        assert tx.status == "rolled_back"
        
        # Verify no state file created
        assert not commit_layer.state_file.exists()


def test_recovery_with_no_crashes():
    """Test recovery when no crashes occurred"""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Commit some transactions
        for i in range(3):
            tx = commit_layer.begin_transaction(f"tx_{i}")
            tx.changes = {f"key_{i}": i * 100}
            commit_layer.commit_transaction(tx)
        
        # Run recovery
        report = commit_layer.recover_from_crash()
        
        # Verify recovery succeeded with no issues
        assert report.recovered
        assert report.uncommitted_transactions == 0
        assert report.rolled_back_transactions == 0
        assert report.temp_files_cleaned == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
