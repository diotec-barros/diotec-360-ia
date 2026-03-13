"""
Test Crash Recovery Protocol

This test verifies the crash recovery implementation for RVC-003 mitigation.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from diotec360.consensus.atomic_commit import AtomicCommitLayer, Transaction


def test_crash_recovery_basic():
    """Test basic crash recovery with uncommitted transactions"""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Create and commit a transaction
        tx1 = acl.begin_transaction("tx1")
        tx1.changes = {"balance": 1000}
        acl.commit_transaction(tx1)
        
        # Create an uncommitted transaction (simulate crash)
        tx2 = acl.begin_transaction("tx2")
        tx2.changes = {"balance": 2000}
        
        # Write to WAL but don't commit
        acl.wal.append_entry(tx2.tx_id, tx2.changes)
        
        # Create temp file (simulate partial write)
        temp_file = state_dir / f"state.{tx2.tx_id}.tmp"
        with open(temp_file, 'w') as f:
            json.dump({"balance": 2000}, f)
        
        # Simulate crash and recovery
        acl2 = AtomicCommitLayer(state_dir, wal_dir)
        report = acl2.recover_from_crash()
        
        # Verify recovery
        assert report.recovered, "Recovery should succeed"
        assert report.uncommitted_transactions == 1, "Should find 1 uncommitted transaction"
        assert report.rolled_back_transactions == 1, "Should rollback 1 transaction"
        assert report.temp_files_cleaned >= 1, "Should clean up temp file"
        assert report.merkle_root_verified, "Merkle root should be verified"
        assert len(report.audit_log) > 0, "Audit log should not be empty"
        
        # Verify state is correct (should be tx1, not tx2)
        state = acl2._load_state()
        assert state["balance"] == 1000, "State should reflect committed transaction only"
        
        print("✓ Basic crash recovery test passed")


def test_crash_recovery_orphaned_files():
    """Test cleanup of orphaned temp files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Create orphaned temp files (no WAL entries)
        orphan1 = state_dir / "state.orphan1.tmp"
        orphan2 = state_dir / "state.orphan2.tmp"
        
        with open(orphan1, 'w') as f:
            json.dump({"test": 1}, f)
        with open(orphan2, 'w') as f:
            json.dump({"test": 2}, f)
        
        # Recover
        report = acl.recover_from_crash()
        
        # Verify cleanup
        assert report.recovered, "Recovery should succeed"
        assert report.temp_files_cleaned == 2, "Should clean up 2 orphaned files"
        assert not orphan1.exists(), "Orphan1 should be deleted"
        assert not orphan2.exists(), "Orphan2 should be deleted"
        
        print("✓ Orphaned files cleanup test passed")


def test_crash_recovery_audit_log():
    """Test audit logging during recovery"""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Create uncommitted transaction
        tx = acl.begin_transaction("tx1")
        tx.changes = {"test": "value"}
        acl.wal.append_entry(tx.tx_id, tx.changes)
        
        # Recover
        report = acl.recover_from_crash()
        
        # Verify audit log
        assert len(report.audit_log) > 0, "Audit log should not be empty"
        
        # Check for key operations in audit log
        audit_text = "\n".join(report.audit_log)
        assert "RECOVERY_START" in audit_text, "Should log recovery start"
        assert "SCAN_WAL" in audit_text, "Should log WAL scan"
        assert "ROLLBACK_TX" in audit_text, "Should log transaction rollback"
        assert "RECOVERY_SUCCESS" in audit_text, "Should log recovery success"
        assert "RECOVERY_END" in audit_text, "Should log recovery end"
        
        # Verify audit log file was written
        audit_file = state_dir / "recovery_audit.log"
        assert audit_file.exists(), "Audit log file should exist"
        
        with open(audit_file, 'r') as f:
            audit_content = f.read()
            assert "Recovery Report" in audit_content, "Audit file should contain report"
            assert "Uncommitted Transactions: 1" in audit_content, "Should log uncommitted count"
        
        print("✓ Audit logging test passed")


def test_crash_recovery_empty_state():
    """Test recovery when no state file exists"""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        # Create atomic commit layer (no state file)
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Recover
        report = acl.recover_from_crash()
        
        # Verify recovery
        assert report.recovered, "Recovery should succeed"
        assert report.merkle_root_verified, "Merkle root should be verified"
        
        # Verify empty state was created
        state = acl._load_state()
        assert state == {}, "State should be empty"
        
        print("✓ Empty state recovery test passed")


def test_crash_recovery_multiple_uncommitted():
    """Test recovery with multiple uncommitted transactions"""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Create multiple uncommitted transactions
        for i in range(5):
            tx = acl.begin_transaction(f"tx{i}")
            tx.changes = {f"key{i}": f"value{i}"}
            acl.wal.append_entry(tx.tx_id, tx.changes)
            
            # Create temp file for some
            if i % 2 == 0:
                temp_file = state_dir / f"state.{tx.tx_id}.tmp"
                with open(temp_file, 'w') as f:
                    json.dump(tx.changes, f)
        
        # Recover
        report = acl.recover_from_crash()
        
        # Verify recovery
        assert report.recovered, "Recovery should succeed"
        assert report.uncommitted_transactions == 5, "Should find 5 uncommitted transactions"
        assert report.rolled_back_transactions == 5, "Should rollback 5 transactions"
        assert report.temp_files_cleaned == 3, "Should clean up 3 temp files"
        
        print("✓ Multiple uncommitted transactions test passed")


if __name__ == "__main__":
    print("Testing Crash Recovery Protocol...")
    print()
    
    test_crash_recovery_basic()
    test_crash_recovery_orphaned_files()
    test_crash_recovery_audit_log()
    test_crash_recovery_empty_state()
    test_crash_recovery_multiple_uncommitted()
    
    print()
    print("=" * 80)
    print("All crash recovery tests passed! ✓")
    print("=" * 80)
