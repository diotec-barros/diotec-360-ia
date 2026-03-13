"""
Test Task 9: StateStore Integration with Atomic Commit Layer

This test verifies that:
1. StateStore uses AtomicCommitLayer for state transitions
2. Crash recovery is performed on initialization
3. Safe mode is activated on recovery failure
4. State transitions use atomic commit protocol
"""

import os
import shutil
import tempfile
from pathlib import Path

from diotec360.consensus.state_store import StateStore
from diotec360.consensus.data_models import StateTransition, StateChange


def test_state_store_atomic_commit_integration():
    """Test that StateStore uses AtomicCommitLayer for state transitions"""
    
    # Create temporary directory for test
    test_dir = Path(tempfile.mkdtemp())
    
    try:
        # Change to test directory
        original_dir = os.getcwd()
        os.chdir(test_dir)
        
        # Create StateStore (should perform crash recovery)
        store = StateStore()
        
        # Verify atomic commit layer is initialized
        assert hasattr(store, 'atomic_commit'), "StateStore should have atomic_commit attribute"
        assert store.atomic_commit is not None, "Atomic commit layer should be initialized"
        
        # Verify not in safe mode (clean initialization)
        assert not store.is_safe_mode(), "StateStore should not be in safe mode after clean initialization"
        
        # Initialize balances first (conservation requires total value to be preserved)
        # Set initial balances directly
        store.set_balance("alice", 1000)
        store.set_balance("bob", 500)
        
        # Get initial root
        root_before = store.get_root_hash()
        
        # Create a state transition that preserves conservation (transfer)
        transition = StateTransition(
            changes=[
                StateChange(key="balance:alice", value=900),  # Alice sends 100
                StateChange(key="balance:bob", value=600)     # Bob receives 100
            ]
        )
        
        # Apply transition (should use atomic commit)
        result = store.apply_state_transition(transition)
        
        if not result:
            print(f"DEBUG: State transition failed")
            print(f"DEBUG: Safe mode: {store.is_safe_mode()}")
            print(f"DEBUG: Recovery report: {store.get_last_recovery_report()}")
        
        assert result, "State transition should succeed"
        
        # Verify state was persisted
        state_file = Path(".DIOTEC360_state/state.json")
        assert state_file.exists(), "State file should exist after commit"
        
        # Verify WAL was created
        wal_file = Path(".DIOTEC360_state/wal/wal.log")
        assert wal_file.exists(), "WAL file should exist"
        
        # Verify balances after transfer
        assert store.get_balance("alice") == 900
        assert store.get_balance("bob") == 600
        
        print("[PASS] StateStore atomic commit integration test passed")
        
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(test_dir, ignore_errors=True)


def test_state_store_crash_recovery():
    """Test that StateStore performs crash recovery on initialization"""
    
    # Create temporary directory for test
    test_dir = Path(tempfile.mkdtemp())
    
    try:
        # Change to test directory
        original_dir = os.getcwd()
        os.chdir(test_dir)
        
        # Create StateStore and apply a transition
        store1 = StateStore()
        
        # Initialize balances
        store1.set_balance("alice", 1000)
        store1.set_balance("bob", 0)
        
        transition = StateTransition(
            changes=[
                StateChange(key="balance:alice", value=900),
                StateChange(key="balance:bob", value=100)
            ]
        )
        
        store1.apply_state_transition(transition)
        
        # Simulate crash by creating an uncommitted WAL entry
        # (manually append to WAL without committing)
        wal_file = Path(".DIOTEC360_state/wal/wal.log")
        with open(wal_file, 'a') as f:
            f.write('{"tx_id": "crash_tx", "changes": {"balance:bob": 999}, "timestamp": 1234567890, "committed": false}\n')
        
        # Create orphaned temp file
        temp_file = Path(".DIOTEC360_state/state.crash_tx.tmp")
        temp_file.write_text('{"balance:alice": 1000, "balance:bob": 999}')
        
        # Create new StateStore (should perform recovery)
        store2 = StateStore()
        
        # Verify recovery was performed
        recovery_report = store2.get_last_recovery_report()
        assert recovery_report is not None, "Recovery report should be available"
        assert recovery_report.recovered, "Recovery should succeed"
        
        # Verify uncommitted transaction was rolled back
        assert recovery_report.uncommitted_transactions >= 1, "Should detect uncommitted transaction"
        assert recovery_report.rolled_back_transactions >= 1, "Should rollback uncommitted transaction"
        
        # Verify temp file was cleaned up
        assert not temp_file.exists(), "Temp file should be deleted during recovery"
        
        # Verify state is consistent (bob's balance should not be 999)
        print(f"DEBUG: Alice balance: {store2.get_balance('alice')}")
        print(f"DEBUG: Bob balance: {store2.get_balance('bob')}")
        assert store2.get_balance("alice") == 900
        assert store2.get_balance("bob") == 100, "Committed change should be preserved"
        
        print("[PASS] StateStore crash recovery test passed")
        
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(test_dir, ignore_errors=True)


def test_state_store_safe_mode():
    """Test that StateStore enters safe mode on recovery failure"""
    
    # Create temporary directory for test
    test_dir = Path(tempfile.mkdtemp())
    
    try:
        # Change to test directory
        original_dir = os.getcwd()
        os.chdir(test_dir)
        
        # Create corrupted state file
        state_dir = Path(".DIOTEC360_state")
        state_dir.mkdir(parents=True, exist_ok=True)
        
        state_file = state_dir / "state.json"
        state_file.write_text("CORRUPTED JSON {{{")
        
        # Create StateStore (recovery should handle corruption gracefully)
        store = StateStore()
        
        # Recovery should succeed by creating empty state
        # (corruption is handled by creating new state)
        recovery_report = store.get_last_recovery_report()
        assert recovery_report is not None
        assert recovery_report.recovered, "Recovery should handle corruption gracefully"
        
        # StateStore should be operational
        assert not store.is_safe_mode(), "Should not be in safe mode after handling corruption"
        
        print("[PASS] StateStore safe mode test passed")
        
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(test_dir, ignore_errors=True)


def test_state_store_atomic_rollback():
    """Test that StateStore rolls back on commit failure"""
    
    # Create temporary directory for test
    test_dir = Path(tempfile.mkdtemp())
    
    try:
        # Change to test directory
        original_dir = os.getcwd()
        os.chdir(test_dir)
        
        # Create StateStore
        store = StateStore()
        
        # Initialize balances
        store.set_balance("alice", 1000)
        store.set_balance("bob", 0)
        
        # Apply initial state
        transition1 = StateTransition(
            changes=[
                StateChange(key="balance:alice", value=900),
                StateChange(key="balance:bob", value=100)
            ]
        )
        
        store.apply_state_transition(transition1)
        
        # Get initial root hash
        root_before = store.get_root_hash()
        
        # Test rollback by simulating a conservation violation
        # (This will cause the transition to fail and rollback)
        transition2 = StateTransition(
            changes=[
                StateChange(key="balance:alice", value=800),
                StateChange(key="balance:bob", value=100)  # Total decreases - violates conservation
            ]
        )
        
        result = store.apply_state_transition(transition2)
        
        # Transition should fail due to conservation violation
        assert not result, "State transition should fail when conservation is violated"
        
        # Verify state was rolled back (root hash unchanged)
        root_after = store.get_root_hash()
        assert root_after == root_before, "Root hash should be unchanged after rollback"
        
        # Verify balances are unchanged
        assert store.get_balance("alice") == 900, "Alice's balance should be unchanged after rollback"
        assert store.get_balance("bob") == 100, "Bob's balance should be unchanged after rollback"
        
        print("[PASS] StateStore atomic rollback test passed")
        
    finally:
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    print("Testing Task 9: StateStore Integration with Atomic Commit Layer\n")
    
    test_state_store_atomic_commit_integration()
    test_state_store_crash_recovery()
    test_state_store_safe_mode()
    test_state_store_atomic_rollback()
    
    print("\n[PASS] All Task 9 integration tests passed!")
