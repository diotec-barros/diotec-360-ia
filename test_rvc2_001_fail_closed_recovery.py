"""
Test RVC2-001: Fail-Closed Recovery

This test verifies that corrupted state.json triggers StateCorruptionPanic
instead of silently creating empty state.

Requirements:
- Corrupted state.json triggers StateCorruptionPanic exception
- Missing state.json triggers StateCorruptionPanic exception
- System refuses to boot with corrupted state
- Clear error message guides administrator to backup restoration
- Zero tolerance for data amnesia
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from diotec360.consensus.atomic_commit import AtomicCommitLayer
from diotec360.core.integrity_panic import StateCorruptionPanic


def test_corrupted_state_json_triggers_panic():
    """
    Test that corrupted state.json triggers StateCorruptionPanic.
    
    This is the core requirement of RVC2-001: the system MUST panic
    instead of creating empty state when corruption is detected.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create a corrupted state.json file (invalid JSON)
        state_file = state_dir / "state.json"
        with open(state_file, 'w') as f:
            f.write("{ this is not valid JSON }")
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Attempt recovery - should raise StateCorruptionPanic
        with pytest.raises(StateCorruptionPanic) as exc_info:
            acl.recover_from_crash()
        
        # Verify exception details
        panic = exc_info.value
        assert panic.violation_type == "STATE_FILE_CORRUPTED"
        assert "path" in panic.details
        assert str(state_file) in panic.details["path"]
        assert "error" in panic.details
        assert panic.recovery_hint is not None
        assert "Genesis Vault" in panic.recovery_hint or "backup" in panic.recovery_hint.lower()
        
        print("✓ Corrupted state.json triggers StateCorruptionPanic")


def test_missing_state_json_triggers_panic():
    """
    Test that missing state.json triggers StateCorruptionPanic.
    
    The system should NOT automatically create empty state when the
    state file is missing. This prevents data amnesia.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Do NOT create state.json - it's missing
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Attempt recovery - should raise StateCorruptionPanic
        with pytest.raises(StateCorruptionPanic) as exc_info:
            acl.recover_from_crash()
        
        # Verify exception details
        panic = exc_info.value
        assert panic.violation_type == "STATE_FILE_MISSING"
        assert "path" in panic.details
        assert "state_dir" in panic.details
        assert panic.recovery_hint is not None
        assert "Genesis Vault" in panic.recovery_hint or "backup" in panic.recovery_hint.lower()
        
        print("✓ Missing state.json triggers StateCorruptionPanic")


def test_partial_json_corruption_triggers_panic():
    """
    Test that partially corrupted JSON triggers StateCorruptionPanic.
    
    Even if the file starts with valid JSON but is truncated or
    malformed, the system should panic.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create a partially corrupted state.json (truncated)
        state_file = state_dir / "state.json"
        with open(state_file, 'w') as f:
            f.write('{"balance": 1000, "account": "test')  # Truncated JSON
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Attempt recovery - should raise StateCorruptionPanic
        with pytest.raises(StateCorruptionPanic) as exc_info:
            acl.recover_from_crash()
        
        # Verify exception details
        panic = exc_info.value
        assert panic.violation_type == "STATE_FILE_CORRUPTED"
        assert "error" in panic.details
        assert panic.recovery_hint is not None
        
        print("✓ Partial JSON corruption triggers StateCorruptionPanic")


def test_empty_file_triggers_panic():
    """
    Test that empty state.json file triggers StateCorruptionPanic.
    
    An empty file is considered corrupted and should trigger panic.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create an empty state.json file
        state_file = state_dir / "state.json"
        state_file.touch()  # Create empty file
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Attempt recovery - should raise StateCorruptionPanic
        with pytest.raises(StateCorruptionPanic) as exc_info:
            acl.recover_from_crash()
        
        # Verify exception details
        panic = exc_info.value
        assert panic.violation_type == "STATE_FILE_CORRUPTED"
        
        print("✓ Empty file triggers StateCorruptionPanic")


def test_panic_includes_recovery_guidance():
    """
    Test that StateCorruptionPanic includes clear recovery guidance.
    
    The exception should provide actionable steps for administrators
    to restore from backup.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create corrupted state
        state_file = state_dir / "state.json"
        with open(state_file, 'w') as f:
            f.write("corrupted")
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Attempt recovery
        with pytest.raises(StateCorruptionPanic) as exc_info:
            acl.recover_from_crash()
        
        panic = exc_info.value
        
        # Verify recovery guidance is comprehensive
        recovery_hint = panic.recovery_hint.lower()
        
        # Should mention backup/restore
        assert any(word in recovery_hint for word in ["backup", "restore", "genesis vault"])
        
        # Should provide actionable steps
        assert any(word in recovery_hint for word in ["run", "command", "action", "step"])
        
        # Should be clear about severity
        assert any(word in recovery_hint for word in ["immediate", "required", "critical"])
        
        print("✓ Panic includes comprehensive recovery guidance")


def test_panic_includes_forensic_metadata():
    """
    Test that StateCorruptionPanic includes forensic metadata.
    
    The exception should capture diagnostic information for
    investigation and audit purposes.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create corrupted state
        state_file = state_dir / "state.json"
        with open(state_file, 'w') as f:
            f.write("corrupted")
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Attempt recovery
        with pytest.raises(StateCorruptionPanic) as exc_info:
            acl.recover_from_crash()
        
        panic = exc_info.value
        
        # Verify forensic metadata
        assert hasattr(panic, 'timestamp')
        assert hasattr(panic, 'forensic_metadata')
        assert panic.timestamp > 0
        
        # Verify metadata structure
        metadata = panic.forensic_metadata
        assert 'timestamp_iso' in metadata
        assert 'system' in metadata
        assert 'process' in metadata
        assert 'stack_trace' in metadata
        
        print("✓ Panic includes forensic metadata")


def test_valid_state_does_not_panic():
    """
    Test that valid state.json does NOT trigger panic.
    
    This is a sanity check to ensure we only panic on actual corruption,
    not on valid state files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create a valid state.json file
        state_file = state_dir / "state.json"
        valid_state = {"balance": 1000, "account": "test"}
        with open(state_file, 'w') as f:
            json.dump(valid_state, f)
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Recovery should succeed without panic
        report = acl.recover_from_crash()
        
        # Verify recovery succeeded
        assert report.recovered
        
        # Verify state was loaded correctly
        loaded_state = acl._load_state()
        assert loaded_state["balance"] == 1000
        assert loaded_state["account"] == "test"
        
        print("✓ Valid state does not trigger panic")


def test_merkle_root_mismatch_triggers_panic():
    """
    Test that Merkle Root mismatch triggers MerkleRootMismatchPanic.
    
    This is a core requirement of RVC2-001: the system MUST panic
    when the stored Merkle Root doesn't match the computed value.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create a valid state.json file
        state_file = state_dir / "state.json"
        valid_state = {"balance": 1000, "account": "test"}
        with open(state_file, 'w') as f:
            json.dump(valid_state, f)
        
        # Create a mock MerkleTree that returns a different root
        class MockMerkleTree:
            def get_root_hash(self):
                # Return a different hash than what will be calculated
                return "0000000000000000000000000000000000000000000000000000000000000000"
        
        # Create atomic commit layer with mock MerkleTree
        acl = AtomicCommitLayer(state_dir, wal_dir, merkle_tree=MockMerkleTree())
        
        # Attempt recovery - should raise MerkleRootMismatchPanic
        from diotec360.core.integrity_panic import MerkleRootMismatchPanic
        with pytest.raises(MerkleRootMismatchPanic) as exc_info:
            acl.recover_from_crash()
        
        # Verify exception details
        panic = exc_info.value
        assert panic.violation_type == "MERKLE_ROOT_MISMATCH"
        assert "computed_root" in panic.details
        assert "stored_root" in panic.details
        assert panic.details["stored_root"] == "0000000000000000000000000000000000000000000000000000000000000000"
        assert "state_file" in panic.details
        assert panic.recovery_hint is not None
        assert "backup" in panic.recovery_hint.lower() or "restore" in panic.recovery_hint.lower()
        
        print("✓ Merkle Root mismatch triggers MerkleRootMismatchPanic")


def test_merkle_root_match_succeeds():
    """
    Test that matching Merkle Root allows recovery to succeed.
    
    This verifies that the Merkle Root verification doesn't cause
    false positives when the state is actually valid.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create a valid state.json file
        state_file = state_dir / "state.json"
        valid_state = {"balance": 1000, "account": "test"}
        with open(state_file, 'w') as f:
            json.dump(valid_state, f)
        
        # Create atomic commit layer to calculate the correct root
        acl_temp = AtomicCommitLayer(state_dir, wal_dir)
        correct_root = acl_temp._calculate_merkle_root(valid_state)
        
        # Create a mock MerkleTree that returns the correct root
        class MockMerkleTree:
            def __init__(self, root):
                self.root = root
            
            def get_root_hash(self):
                return self.root
        
        # Create atomic commit layer with mock MerkleTree
        acl = AtomicCommitLayer(state_dir, wal_dir, merkle_tree=MockMerkleTree(correct_root))
        
        # Recovery should succeed
        report = acl.recover_from_crash()
        
        # Verify recovery succeeded
        assert report.recovered
        assert report.merkle_root_verified
        assert report.merkle_root == correct_root
        
        # Verify state was loaded correctly
        loaded_state = acl._load_state()
        assert loaded_state["balance"] == 1000
        assert loaded_state["account"] == "test"
        
        print("✓ Matching Merkle Root allows recovery to succeed")


def test_merkle_root_panic_includes_diagnostic_info():
    """
    Test that MerkleRootMismatchPanic includes comprehensive diagnostic info.
    
    The exception should provide enough information for administrators
    to investigate the integrity violation.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create a valid state.json file
        state_file = state_dir / "state.json"
        valid_state = {"balance": 1000, "account": "test", "nonce": 42}
        with open(state_file, 'w') as f:
            json.dump(valid_state, f)
        
        # Create a mock MerkleTree that returns a different root
        class MockMerkleTree:
            def get_root_hash(self):
                return "tampered_root_hash"
        
        # Create atomic commit layer with mock MerkleTree
        acl = AtomicCommitLayer(state_dir, wal_dir, merkle_tree=MockMerkleTree())
        
        # Attempt recovery
        from diotec360.core.integrity_panic import MerkleRootMismatchPanic
        with pytest.raises(MerkleRootMismatchPanic) as exc_info:
            acl.recover_from_crash()
        
        panic = exc_info.value
        
        # Verify diagnostic information
        assert "computed_root" in panic.details
        assert "stored_root" in panic.details
        assert panic.details["stored_root"] == "tampered_root_hash"
        assert "state_file" in panic.details
        assert "state_size" in panic.details
        assert panic.details["state_size"] == 3  # balance, account, nonce
        assert "state_keys" in panic.details
        assert set(panic.details["state_keys"]) == {"balance", "account", "nonce"}
        
        # Verify forensic metadata
        assert hasattr(panic, 'timestamp')
        assert hasattr(panic, 'forensic_metadata')
        assert panic.timestamp > 0
        
        print("✓ Merkle Root panic includes comprehensive diagnostic info")


def test_panic_serialization():
    """
    Test that StateCorruptionPanic can be serialized for logging.
    
    The exception should be serializable to JSON for audit trails
    and monitoring systems.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / "state"
        wal_dir = Path(tmpdir) / "wal"
        state_dir.mkdir(parents=True)
        wal_dir.mkdir(parents=True)
        
        # Create corrupted state
        state_file = state_dir / "state.json"
        with open(state_file, 'w') as f:
            f.write("corrupted")
        
        # Create atomic commit layer
        acl = AtomicCommitLayer(state_dir, wal_dir)
        
        # Attempt recovery
        with pytest.raises(StateCorruptionPanic) as exc_info:
            acl.recover_from_crash()
        
        panic = exc_info.value
        
        # Test serialization
        panic_dict = panic.to_dict()
        assert isinstance(panic_dict, dict)
        assert 'violation_type' in panic_dict
        assert 'details' in panic_dict
        assert 'recovery_hint' in panic_dict
        
        # Test JSON serialization
        panic_json = panic.to_json()
        assert isinstance(panic_json, str)
        
        # Verify JSON is valid
        parsed = json.loads(panic_json)
        assert parsed['violation_type'] == "STATE_FILE_CORRUPTED"
        
        print("✓ Panic can be serialized for logging")


if __name__ == "__main__":
    print("Testing RVC2-001: Fail-Closed Recovery")
    print("=" * 80)
    print()
    
    # Run tests
    test_corrupted_state_json_triggers_panic()
    test_missing_state_json_triggers_panic()
    test_partial_json_corruption_triggers_panic()
    test_empty_file_triggers_panic()
    test_panic_includes_recovery_guidance()
    test_panic_includes_forensic_metadata()
    test_valid_state_does_not_panic()
    test_merkle_root_mismatch_triggers_panic()
    test_merkle_root_match_succeeds()
    test_merkle_root_panic_includes_diagnostic_info()
    test_panic_serialization()
    
    print()
    print("=" * 80)
    print("All RVC2-001 tests passed! ✓")
    print("System now implements fail-closed recovery:")
    print("  - Corrupted state → StateCorruptionPanic")
    print("  - Missing state → StateCorruptionPanic")
    print("  - Merkle Root mismatch → MerkleRootMismatchPanic")
    print("  - Zero tolerance for data amnesia")
    print("=" * 80)
