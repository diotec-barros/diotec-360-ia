"""
Test Inquisitor Attack 1: WAL Corruption Resilience

This test proves that the system does NOT crash when the WAL file
contains corrupted JSON entries.
"""

import pytest
import tempfile
from pathlib import Path

from diotec360.consensus.atomic_commit import WriteAheadLog, AtomicCommitLayer


def test_wal_corrupted_json_does_not_crash():
    """
    INQUISITOR ATTACK 1: WAL Corruption
    
    Scenario: WAL file contains corrupted JSON (simulating crash during write)
    Expected: System skips corrupted entries and continues recovery
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        wal_dir = Path(tmpdir)
        wal = WriteAheadLog(wal_dir)
        
        # Write valid entry
        wal.append_entry("tx_valid", {"key": "value"})
        
        # Manually corrupt the WAL file by appending malformed JSON
        with open(wal.wal_file, 'a') as f:
            f.write('{"tx_id": "corrupted", "incomplete_json\n')  # Malformed!
            f.write('not even json at all\n')  # Completely invalid!
        
        # Try to read entries - should NOT crash
        entries = wal._read_all_entries()
        
        # Should have skipped corrupted entries and returned only valid one
        assert len(entries) == 1
        assert entries[0].tx_id == "tx_valid"
        
        print("✅ ATTACK 1 BLOCKED: System survived corrupted WAL")


def test_recovery_with_corrupted_wal():
    """
    INQUISITOR ATTACK 1: Recovery with Corrupted WAL
    
    Scenario: System crashes during WAL write, then restarts
    Expected: Recovery succeeds despite corrupted WAL
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        commit_layer = AtomicCommitLayer(state_dir, wal_dir)
        
        # Write some valid transactions
        for i in range(3):
            tx = commit_layer.begin_transaction(f"tx_{i}")
            tx.changes = {f"key_{i}": i * 100}
            commit_layer.commit_transaction(tx)
        
        # Corrupt the WAL file
        with open(commit_layer.wal.wal_file, 'a') as f:
            f.write('{"corrupted": incomplete\n')
        
        # Simulate restart - create new commit layer
        commit_layer2 = AtomicCommitLayer(state_dir, wal_dir)
        
        # Run recovery - should NOT crash
        report = commit_layer2.recover_from_crash()
        
        # Recovery should succeed
        assert report.recovered, "Recovery should succeed despite corrupted WAL"
        
        print("✅ ATTACK 1 BLOCKED: Recovery succeeded with corrupted WAL")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
