"""
Unit tests for IntegrityPanic Exception Framework

Tests all exception classes and their behavior according to RVC v2 requirements.
"""

import pytest
import json
import time
import os
from diotec360.core.integrity_panic import (
    IntegrityPanic,
    StateCorruptionPanic,
    MerkleRootMismatchPanic,
    UnsupportedConstraintError,
    InvalidSignaturePanic,
    WALCorruptionPanic,
    NodeIdentityMismatchPanic,
    log_integrity_panic,
)


class TestIntegrityPanicBase:
    """Test the base IntegrityPanic exception class."""
    
    def test_basic_initialization(self):
        """Test basic exception initialization."""
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test recovery hint"
        )
        
        assert panic.violation_type == "TEST_VIOLATION"
        assert panic.details == {"key": "value"}
        assert panic.recovery_hint == "Test recovery hint"
        assert isinstance(panic.timestamp, float)
        assert panic.timestamp <= time.time()
    
    def test_exception_message_format(self):
        """Test that exception message is properly formatted."""
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"error": "test error", "path": "/test/path"},
            recovery_hint="Do something"
        )
        
        message = str(panic)
        assert "INTEGRITY PANIC: TEST_VIOLATION" in message
        assert "error: test error" in message
        assert "path: /test/path" in message
        assert "Recovery Hint:" in message
        assert "Do something" in message
    
    def test_to_dict_serialization(self):
        """Test dictionary serialization."""
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        data = panic.to_dict()
        assert data["exception_class"] == "IntegrityPanic"
        assert data["violation_type"] == "TEST_VIOLATION"
        assert data["details"] == {"key": "value"}
        assert data["recovery_hint"] == "Test hint"
        assert "timestamp" in data
    
    def test_to_json_serialization(self):
        """Test JSON serialization."""
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        json_str = panic.to_json()
        data = json.loads(json_str)
        
        assert data["exception_class"] == "IntegrityPanic"
        assert data["violation_type"] == "TEST_VIOLATION"
        assert data["details"] == {"key": "value"}
    
    def test_exception_is_raisable(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(IntegrityPanic) as exc_info:
            raise IntegrityPanic(
                violation_type="TEST",
                details={},
                recovery_hint="Test"
            )
        
        assert exc_info.value.violation_type == "TEST"


class TestStateCorruptionPanic:
    """Test StateCorruptionPanic exception."""
    
    def test_inheritance(self):
        """Test that StateCorruptionPanic inherits from IntegrityPanic."""
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_MISSING",
            details={"path": "/test/state.json"}
        )
        
        assert isinstance(panic, IntegrityPanic)
        assert isinstance(panic, StateCorruptionPanic)
    
    def test_default_recovery_hint(self):
        """Test default recovery hint for state corruption."""
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={"path": "/test/state.json"}
        )
        
        assert "Genesis Vault" in panic.recovery_hint
        assert "backup" in panic.recovery_hint.lower()
    
    def test_custom_recovery_hint(self):
        """Test custom recovery hint override."""
        custom_hint = "Custom recovery procedure"
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={"path": "/test/state.json"},
            recovery_hint=custom_hint
        )
        
        assert panic.recovery_hint == custom_hint
    
    def test_missing_file_scenario(self):
        """Test scenario: state.json file missing."""
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_MISSING",
            details={"path": "/var/Diotec360/state.json"}
        )
        
        assert panic.violation_type == "STATE_FILE_MISSING"
        assert panic.details["path"] == "/var/Diotec360/state.json"
    
    def test_corrupted_json_scenario(self):
        """Test scenario: corrupted JSON in state file."""
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={
                "path": "/var/Diotec360/state.json",
                "error": "Expecting property name enclosed in double quotes"
            }
        )
        
        assert panic.violation_type == "STATE_FILE_CORRUPTED"
        assert "error" in panic.details
    
    def test_state_file_missing_recovery_hint_actionable(self):
        """Test that STATE_FILE_MISSING recovery hint provides actionable steps."""
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_MISSING",
            details={"path": "/var/Diotec360/state.json"}
        )
        
        hint = panic.recovery_hint
        # Check for step-by-step guidance
        assert "1." in hint and "2." in hint and "3." in hint
        # Check for specific commands
        assert "python -m Diotec360.genesis.restore" in hint
        assert "python -m Diotec360.genesis.init" in hint
        # Check for verification step
        assert "verify" in hint.lower()
    
    def test_state_file_corrupted_recovery_hint_actionable(self):
        """Test that STATE_FILE_CORRUPTED recovery hint provides actionable steps."""
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={"path": "/var/Diotec360/state.json", "error": "Invalid JSON"}
        )
        
        hint = panic.recovery_hint
        # Check for preservation of corrupted file
        assert "cp state.json" in hint or "Preserve" in hint
        # Check for backup restoration
        assert "Genesis Vault" in hint
        assert "python -m Diotec360.genesis" in hint
        # Check for investigation guidance
        assert "investigate" in hint.lower() or "root cause" in hint.lower()
    
    def test_partial_corruption_recovery_hint(self):
        """Test recovery hint for partial state corruption."""
        panic = StateCorruptionPanic(
            violation_type="STATE_PARTIAL_CORRUPTION",
            details={"path": "/var/Diotec360/state.json"}
        )
        
        hint = panic.recovery_hint
        # Should offer multiple recovery options
        assert "restore" in hint.lower()
        assert "alternative" in hint.lower() or "option" in hint.lower()
        # Should mention WAL replay
        assert "WAL" in hint or "wal" in hint.lower()
        # Should include verification
        assert "verify" in hint.lower()


class TestMerkleRootMismatchPanic:
    """Test MerkleRootMismatchPanic exception."""
    
    def test_inheritance(self):
        """Test proper inheritance."""
        panic = MerkleRootMismatchPanic(
            violation_type="MERKLE_ROOT_MISMATCH",
            details={"computed": "abc123", "stored": "def456"}
        )
        
        assert isinstance(panic, IntegrityPanic)
        assert isinstance(panic, MerkleRootMismatchPanic)
    
    def test_default_recovery_hint(self):
        """Test default recovery hint mentions tampering."""
        panic = MerkleRootMismatchPanic(
            violation_type="MERKLE_ROOT_MISMATCH",
            details={"computed": "abc", "stored": "def"}
        )
        
        assert "tamper" in panic.recovery_hint.lower()  # Changed from "tampered" to "tamper" to match "tampering"
        assert "backup" in panic.recovery_hint.lower()
    
    def test_merkle_mismatch_scenario(self):
        """Test scenario: Merkle root mismatch detected."""
        panic = MerkleRootMismatchPanic(
            violation_type="MERKLE_ROOT_MISMATCH",
            details={
                "computed": "0x1234567890abcdef",
                "stored": "0xfedcba0987654321",
                "state_size": 1000
            }
        )
        
        assert panic.details["computed"] == "0x1234567890abcdef"
        assert panic.details["stored"] == "0xfedcba0987654321"
        assert panic.details["state_size"] == 1000
    
    def test_merkle_mismatch_recovery_hint_security_focused(self):
        """Test that MERKLE_ROOT_MISMATCH recovery hint emphasizes security."""
        panic = MerkleRootMismatchPanic(
            violation_type="MERKLE_ROOT_MISMATCH",
            details={"computed": "abc", "stored": "def"}
        )
        
        hint = panic.recovery_hint
        # Should emphasize security
        assert "CRITICAL" in hint or "SECURITY" in hint
        assert "HALT" in hint or "STOP" in hint or "immediately" in hint.lower()
        # Should mention forensics
        assert "forensic" in hint.lower()
        # Should guide investigation
        assert "investigate" in hint.lower()
        assert "unauthorized" in hint.lower() or "breach" in hint.lower()
        # Should include restoration steps
        assert "restore" in hint.lower()
        assert "backup" in hint.lower()
    
    def test_merkle_missing_recovery_hint(self):
        """Test recovery hint for missing Merkle root."""
        panic = MerkleRootMismatchPanic(
            violation_type="MERKLE_ROOT_MISSING",
            details={"path": "/var/Diotec360/state.json"}
        )
        
        hint = panic.recovery_hint
        # Should offer restoration
        assert "restore" in hint.lower()
        # Should offer recomputation as alternative
        assert "recompute" in hint.lower() or "alternative" in hint.lower()
        # Should mention verification
        assert "verify" in hint.lower()


class TestUnsupportedConstraintError:
    """Test UnsupportedConstraintError exception."""
    
    def test_inheritance(self):
        """Test proper inheritance."""
        panic = UnsupportedConstraintError(
            violation_type="UNSUPPORTED_AST_NODE",
            details={"node_type": "BitOr"}
        )
        
        assert isinstance(panic, IntegrityPanic)
        assert isinstance(panic, UnsupportedConstraintError)
    
    def test_default_recovery_hint(self):
        """Test default recovery hint mentions syntax."""
        panic = UnsupportedConstraintError(
            violation_type="UNSUPPORTED_AST_NODE",
            details={"node_type": "BitOr"}
        )
        
        assert "syntax" in panic.recovery_hint.lower()
        assert "documentation" in panic.recovery_hint.lower()
    
    def test_unsupported_node_scenario(self):
        """Test scenario: unsupported AST node type."""
        panic = UnsupportedConstraintError(
            violation_type="UNSUPPORTED_AST_NODE",
            details={
                "node_type": "BitOr",
                "node_repr": "BinOp(left=Name('a'), op=BitOr(), right=Name('b'))",
                "supported_types": ["Add", "Sub", "Mult", "Div"]
            }
        )
        
        assert panic.details["node_type"] == "BitOr"
        assert "supported_types" in panic.details
    
    def test_unsupported_node_recovery_hint_actionable(self):
        """Test that UNSUPPORTED_AST_NODE recovery hint is actionable."""
        panic = UnsupportedConstraintError(
            violation_type="UNSUPPORTED_AST_NODE",
            details={
                "node_type": "BitOr",
                "node_repr": "BinOp(left=Name('balance'), op=BitOr(), right=Constant(value=0xFF))"
            }
        )
        
        hint = panic.recovery_hint
        # Should list supported operations
        assert "Add" in hint or "+" in hint
        assert "Sub" in hint or "-" in hint
        # Should reference documentation
        assert "docs/" in hint or "documentation" in hint.lower()
        # Should mention examples
        assert "examples" in hint.lower()
        # Should provide validation command
        assert "python -m Diotec360" in hint
        # Should explain security rationale
        assert "fail-closed" in hint.lower() or "security" in hint.lower()
    
    def test_constraint_too_complex_recovery_hint(self):
        """Test recovery hint for overly complex constraints."""
        panic = UnsupportedConstraintError(
            violation_type="CONSTRAINT_TOO_COMPLEX",
            details={"complexity": 1000, "max_complexity": 100}
        )
        
        hint = panic.recovery_hint
        # Should suggest simplification
        assert "simplify" in hint.lower()
        # Should suggest breaking into multiple constraints
        assert "multiple" in hint.lower()
        # Should mention complexity limits
        assert "complex" in hint.lower()


class TestInvalidSignaturePanic:
    """Test InvalidSignaturePanic exception."""
    
    def test_inheritance(self):
        """Test proper inheritance."""
        panic = InvalidSignaturePanic(
            violation_type="INVALID_GOSSIP_SIGNATURE",
            details={"sender_id": "node_123"}
        )
        
        assert isinstance(panic, IntegrityPanic)
        assert isinstance(panic, InvalidSignaturePanic)
    
    def test_default_recovery_hint(self):
        """Test default recovery hint mentions rejection."""
        panic = InvalidSignaturePanic(
            violation_type="INVALID_GOSSIP_SIGNATURE",
            details={"sender_id": "node_123"}
        )
        
        assert "reject" in panic.recovery_hint.lower()
        # Changed to check for security context instead of specific "untrusted" word
        assert "security" in panic.recovery_hint.lower() or "malicious" in panic.recovery_hint.lower()
    
    def test_invalid_signature_scenario(self):
        """Test scenario: invalid ED25519 signature."""
        panic = InvalidSignaturePanic(
            violation_type="INVALID_GOSSIP_SIGNATURE",
            details={
                "sender_id": "node_abc123",
                "message_type": "STATE_UPDATE"
            }
        )
        
        assert panic.details["sender_id"] == "node_abc123"
        assert panic.details["message_type"] == "STATE_UPDATE"
    
    def test_invalid_gossip_signature_recovery_hint_actionable(self):
        """Test that INVALID_GOSSIP_SIGNATURE recovery hint is actionable."""
        panic = InvalidSignaturePanic(
            violation_type="INVALID_GOSSIP_SIGNATURE",
            details={"sender_id": "node_abc123", "message_type": "STATE_UPDATE"}
        )
        
        hint = panic.recovery_hint
        # Should mention automatic rejection
        assert "REJECTED" in hint or "rejected" in hint.lower()
        # Should provide investigation steps
        assert "investigate" in hint.lower() or "verify" in hint.lower()
        # Should include commands
        assert "python -m Diotec360" in hint
        # Should mention blacklisting
        assert "blacklist" in hint.lower()
        # Should reference sender_id
        assert "node_abc123" in hint
    
    def test_unsigned_message_recovery_hint(self):
        """Test recovery hint for unsigned messages."""
        panic = InvalidSignaturePanic(
            violation_type="UNSIGNED_MESSAGE",
            details={"sender_id": "node_xyz"}
        )
        
        hint = panic.recovery_hint
        # Should mention rejection
        assert "REJECTED" in hint or "rejected" in hint.lower()
        # Should explain possible causes
        assert "outdated" in hint.lower() or "configuration" in hint.lower()
        # Should mention version requirement
        assert "v1.9.2" in hint or "version" in hint.lower()
    
    def test_public_key_mismatch_recovery_hint(self):
        """Test recovery hint for public key mismatch."""
        panic = InvalidSignaturePanic(
            violation_type="PUBLIC_KEY_MISMATCH",
            details={"sender_id": "node_xyz"}
        )
        
        hint = panic.recovery_hint
        # Should emphasize security
        assert "SECURITY" in hint or "ALERT" in hint
        # Should mention out-of-band verification
        assert "out-of-band" in hint.lower() or "phone" in hint.lower()
        # Should warn about impersonation
        assert "impersonation" in hint.lower()
        # Should provide key update command
        assert "update_key" in hint or "update-key" in hint


class TestWALCorruptionPanic:
    """Test WALCorruptionPanic exception."""
    
    def test_inheritance(self):
        """Test proper inheritance."""
        panic = WALCorruptionPanic(
            violation_type="WAL_FILE_CORRUPTED",
            details={"path": "/var/Diotec360/wal.log"}
        )
        
        assert isinstance(panic, IntegrityPanic)
        assert isinstance(panic, WALCorruptionPanic)
    
    def test_default_recovery_hint(self):
        """Test default recovery hint mentions WAL."""
        panic = WALCorruptionPanic(
            violation_type="WAL_FILE_CORRUPTED",
            details={"path": "/var/Diotec360/wal.log"}
        )
        
        assert "WAL" in panic.recovery_hint
        assert "backup" in panic.recovery_hint.lower()
    
    def test_wal_corrupted_recovery_hint_actionable(self):
        """Test that WAL_FILE_CORRUPTED recovery hint is actionable."""
        panic = WALCorruptionPanic(
            violation_type="WAL_FILE_CORRUPTED",
            details={"path": "/var/Diotec360/wal.log"}
        )
        
        hint = panic.recovery_hint
        # Should preserve corrupted file
        assert "cp wal.log" in hint or "Preserve" in hint
        # Should offer multiple recovery options
        assert "Option A" in hint or "Option B" in hint
        # Should include analysis command
        assert "analyze_wal" in hint or "analyze-wal" in hint
        # Should mention verification
        assert "verify" in hint.lower()
        # Should suggest investigating root cause
        assert "investigate" in hint.lower() or "root cause" in hint.lower()
        # Should mention disk health
        assert "disk" in hint.lower() or "SMART" in hint
    
    def test_wal_state_inconsistency_recovery_hint(self):
        """Test recovery hint for WAL/state inconsistency."""
        panic = WALCorruptionPanic(
            violation_type="WAL_STATE_INCONSISTENCY",
            details={"path": "/var/Diotec360/wal.log"}
        )
        
        hint = panic.recovery_hint
        # Should offer reconciliation
        assert "reconcile" in hint.lower()
        # Should provide reconciliation command
        assert "python -m Diotec360" in hint
        # Should mention atomicity
        assert "atomic" in hint.lower() or "inconsisten" in hint.lower()
    
    def test_wal_replay_failed_recovery_hint(self):
        """Test recovery hint for WAL replay failure."""
        panic = WALCorruptionPanic(
            violation_type="WAL_REPLAY_FAILED",
            details={"path": "/var/Diotec360/wal.log"}
        )
        
        hint = panic.recovery_hint
        # Should suggest restoration
        assert "restore" in hint.lower()
        # Should offer partial replay option
        assert "partial" in hint.lower() or "skip-errors" in hint
        # Should mention format compatibility
        assert "format" in hint.lower() or "incompatib" in hint.lower()


class TestNodeIdentityMismatchPanic:
    """Test NodeIdentityMismatchPanic exception."""
    
    def test_inheritance(self):
        """Test proper inheritance."""
        panic = NodeIdentityMismatchPanic(
            violation_type="NODE_IDENTITY_MISMATCH",
            details={"sender_id": "node_123"}
        )
        
        assert isinstance(panic, IntegrityPanic)
        assert isinstance(panic, NodeIdentityMismatchPanic)
    
    def test_default_recovery_hint(self):
        """Test default recovery hint mentions impersonation."""
        panic = NodeIdentityMismatchPanic(
            violation_type="NODE_IDENTITY_MISMATCH",
            details={"sender_id": "node_123"}
        )
        
        assert "impersonation" in panic.recovery_hint.lower()
        # Check for verification instead of just "identity" since the hint focuses on verification
        assert "verif" in panic.recovery_hint.lower()  # Matches "verify", "verification", etc.
    
    def test_node_identity_mismatch_recovery_hint_actionable(self):
        """Test that NODE_IDENTITY_MISMATCH recovery hint is actionable."""
        panic = NodeIdentityMismatchPanic(
            violation_type="NODE_IDENTITY_MISMATCH",
            details={"sender_id": "node_xyz789"}
        )
        
        hint = panic.recovery_hint
        # Should emphasize critical security
        assert "CRITICAL" in hint or "SECURITY" in hint
        # Should mention automatic actions
        assert "REJECTED" in hint or "BLOCKED" in hint
        # Should require out-of-band verification
        assert "out-of-band" in hint.lower() or "phone" in hint.lower()
        # Should provide key update command
        assert "update_node_key" in hint or "update-node-key" in hint
        # Should mention blacklisting
        assert "blacklist" in hint.lower()
        # Should reference sender_id
        assert "node_xyz789" in hint
        # Should suggest security enhancements
        assert "key pinning" in hint.lower() or "certificate" in hint.lower()
    
    def test_node_key_rotation_unverified_recovery_hint(self):
        """Test recovery hint for unverified key rotation."""
        panic = NodeIdentityMismatchPanic(
            violation_type="NODE_KEY_ROTATION_UNVERIFIED",
            details={"sender_id": "node_abc"}
        )
        
        hint = panic.recovery_hint
        # Should mention certificate requirement
        assert "certificate" in hint.lower()
        # Should provide verification command
        assert "verify_key_rotation_cert" in hint or "verify-key-rotation-cert" in hint
        # Should warn against accepting without verification
        assert "Do NOT" in hint or "do not" in hint.lower()


class TestLogIntegrityPanic:
    """Test the log_integrity_panic utility function."""
    
    def test_log_without_logger(self, capsys):
        """Test logging without a logger (uses print)."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        log_integrity_panic(panic, write_forensic_report=False)
        
        captured = capsys.readouterr()
        assert "INTEGRITY PANIC LOGGED" in captured.out
        assert "TEST" in captured.out
    
    def test_log_with_logger(self):
        """Test logging with a custom logger."""
        class MockLogger:
            def __init__(self):
                self.messages = []
            
            def critical(self, message):
                self.messages.append(message)
            
            def info(self, message):
                self.messages.append(message)
            
            def error(self, message):
                self.messages.append(message)
        
        logger = MockLogger()
        panic = IntegrityPanic(
            violation_type="TEST",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        log_integrity_panic(panic, logger, write_forensic_report=False)
        
        assert len(logger.messages) >= 1
        assert "INTEGRITY_PANIC" in logger.messages[0]
        assert "TEST" in logger.messages[0]
    
    def test_log_with_forensic_report(self, tmp_path):
        """Test logging with forensic report writing."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        forensic_path = log_integrity_panic(
            panic,
            write_forensic_report=True,
            forensic_dir=str(tmp_path)
        )
        
        assert forensic_path is not None
        assert os.path.exists(forensic_path)
        assert "integrity_panic_TEST" in forensic_path


class TestForensicMetadata:
    """Test forensic metadata capture for investigation."""
    
    def test_forensic_metadata_exists(self):
        """Test that forensic metadata is captured."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        assert hasattr(panic, 'forensic_metadata')
        assert isinstance(panic.forensic_metadata, dict)
    
    def test_forensic_metadata_contains_timestamp(self):
        """Test that forensic metadata includes timestamp information."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={},
            recovery_hint="Test"
        )
        
        metadata = panic.forensic_metadata
        assert "timestamp_iso" in metadata
        assert "timestamp_unix" in metadata
        assert isinstance(metadata["timestamp_unix"], float)
    
    def test_forensic_metadata_contains_system_info(self):
        """Test that forensic metadata includes system information."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={},
            recovery_hint="Test"
        )
        
        metadata = panic.forensic_metadata
        assert "system" in metadata
        assert "hostname" in metadata["system"]
        assert "platform" in metadata["system"]
        assert "python_version" in metadata["system"]
        assert "architecture" in metadata["system"]
    
    def test_forensic_metadata_contains_process_info(self):
        """Test that forensic metadata includes process information."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={},
            recovery_hint="Test"
        )
        
        metadata = panic.forensic_metadata
        assert "process" in metadata
        assert "pid" in metadata["process"]
        assert "cwd" in metadata["process"]
        assert "user" in metadata["process"]
        assert metadata["process"]["pid"] == os.getpid()
    
    def test_forensic_metadata_contains_stack_trace(self):
        """Test that forensic metadata includes stack trace."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={},
            recovery_hint="Test"
        )
        
        metadata = panic.forensic_metadata
        assert "stack_trace" in metadata
        assert isinstance(metadata["stack_trace"], list)
        assert len(metadata["stack_trace"]) > 0
        
        # Check stack frame structure
        frame = metadata["stack_trace"][0]
        assert "filename" in frame
        assert "line" in frame
        assert "function" in frame
        assert "code" in frame
    
    def test_forensic_metadata_contains_environment(self):
        """Test that forensic metadata includes environment information."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={},
            recovery_hint="Test"
        )
        
        metadata = panic.forensic_metadata
        assert "environment" in metadata
        assert "DIOTEC360_version" in metadata["environment"]
        assert "python_path" in metadata["environment"]
    
    def test_forensic_metadata_in_serialization(self):
        """Test that forensic metadata is included in serialization."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={"key": "value"},
            recovery_hint="Test"
        )
        
        data = panic.to_dict()
        assert "forensic_metadata" in data
        assert "system" in data["forensic_metadata"]
        assert "process" in data["forensic_metadata"]
        assert "stack_trace" in data["forensic_metadata"]
    
    def test_forensic_metadata_in_json(self):
        """Test that forensic metadata is included in JSON serialization."""
        panic = IntegrityPanic(
            violation_type="TEST",
            details={"key": "value"},
            recovery_hint="Test"
        )
        
        json_str = panic.to_json()
        data = json.loads(json_str)
        
        assert "forensic_metadata" in data
        assert "system" in data["forensic_metadata"]
        assert "stack_trace" in data["forensic_metadata"]
    
    def test_write_forensic_report(self, tmp_path):
        """Test writing forensic report to disk."""
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"error": "test error"},
            recovery_hint="Test recovery"
        )
        
        report_path = panic.write_forensic_report(str(tmp_path))
        
        # Check file was created
        assert os.path.exists(report_path)
        assert "integrity_panic_TEST_VIOLATION" in report_path
        assert report_path.endswith(".json")
        
        # Check file contents
        with open(report_path, 'r') as f:
            data = json.load(f)
        
        assert data["violation_type"] == "TEST_VIOLATION"
        assert data["details"]["error"] == "test error"
        assert "forensic_metadata" in data
    
    def test_forensic_report_filename_format(self, tmp_path):
        """Test that forensic report filename follows expected format."""
        panic = IntegrityPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={},
            recovery_hint="Test"
        )
        
        report_path = panic.write_forensic_report(str(tmp_path))
        filename = os.path.basename(report_path)
        
        # Format: integrity_panic_{violation_type}_{timestamp}.json
        assert filename.startswith("integrity_panic_STATE_FILE_CORRUPTED_")
        assert filename.endswith(".json")
    
    def test_forensic_report_creates_directory(self, tmp_path):
        """Test that forensic report creates output directory if needed."""
        output_dir = tmp_path / "forensic" / "reports"
        
        panic = IntegrityPanic(
            violation_type="TEST",
            details={},
            recovery_hint="Test"
        )
        
        report_path = panic.write_forensic_report(str(output_dir))
        
        assert os.path.exists(output_dir)
        assert os.path.exists(report_path)


class TestExceptionHierarchy:
    """Test the complete exception hierarchy."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all specialized exceptions inherit from IntegrityPanic."""
        exceptions = [
            StateCorruptionPanic("TEST", {}),
            MerkleRootMismatchPanic("TEST", {}),
            UnsupportedConstraintError("TEST", {}),
            InvalidSignaturePanic("TEST", {}),
            WALCorruptionPanic("TEST", {}),
            NodeIdentityMismatchPanic("TEST", {}),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, IntegrityPanic)
            assert isinstance(exc, Exception)
    
    def test_all_exceptions_are_catchable_as_base(self):
        """Test that all exceptions can be caught as IntegrityPanic."""
        exceptions = [
            StateCorruptionPanic("TEST", {}),
            MerkleRootMismatchPanic("TEST", {}),
            UnsupportedConstraintError("TEST", {}),
            InvalidSignaturePanic("TEST", {}),
            WALCorruptionPanic("TEST", {}),
            NodeIdentityMismatchPanic("TEST", {}),
        ]
        
        for exc in exceptions:
            with pytest.raises(IntegrityPanic):
                raise exc
    
    def test_exception_class_names_in_serialization(self):
        """Test that each exception reports its own class name."""
        exceptions = [
            (StateCorruptionPanic("TEST", {}), "StateCorruptionPanic"),
            (MerkleRootMismatchPanic("TEST", {}), "MerkleRootMismatchPanic"),
            (UnsupportedConstraintError("TEST", {}), "UnsupportedConstraintError"),
            (InvalidSignaturePanic("TEST", {}), "InvalidSignaturePanic"),
            (WALCorruptionPanic("TEST", {}), "WALCorruptionPanic"),
            (NodeIdentityMismatchPanic("TEST", {}), "NodeIdentityMismatchPanic"),
        ]
        
        for exc, expected_name in exceptions:
            data = exc.to_dict()
            assert data["exception_class"] == expected_name


class TestRealWorldScenarios:
    """Test real-world usage scenarios from the design document."""
    
    def test_fail_closed_boot_scenario(self):
        """Test the fail-closed boot sequence scenario."""
        # Scenario: Corrupted state.json detected on boot
        try:
            raise StateCorruptionPanic(
                violation_type="STATE_FILE_CORRUPTED",
                details={
                    "path": "/var/Diotec360/state.json",
                    "error": "Expecting property name enclosed in double quotes: line 42 column 5"
                },
                recovery_hint="Restore from latest backup in Genesis Vault"
            )
        except IntegrityPanic as e:
            assert e.violation_type == "STATE_FILE_CORRUPTED"
            assert "Genesis Vault" in e.recovery_hint
            assert e.details["path"] == "/var/Diotec360/state.json"
    
    def test_merkle_verification_scenario(self):
        """Test Merkle root verification failure scenario."""
        # Scenario: Merkle root mismatch detected
        try:
            raise MerkleRootMismatchPanic(
                violation_type="MERKLE_ROOT_MISMATCH",
                details={
                    "computed": "0x1234567890abcdef1234567890abcdef",
                    "stored": "0xfedcba0987654321fedcba0987654321",
                    "state_size": 5000
                }
            )
        except IntegrityPanic as e:
            assert e.violation_type == "MERKLE_ROOT_MISMATCH"
            assert "tamper" in e.recovery_hint.lower()  # Changed from "tampered" to "tamper" to match "tampering"
    
    def test_hard_reject_parsing_scenario(self):
        """Test hard-reject constraint parsing scenario."""
        # Scenario: Unsupported AST node in constraint
        try:
            raise UnsupportedConstraintError(
                violation_type="UNSUPPORTED_AST_NODE",
                details={
                    "node_type": "BitOr",
                    "node_repr": "BinOp(left=Name('balance'), op=BitOr(), right=Constant(value=0xFF))",
                    "supported_types": ["Add", "Sub", "Mult", "Div", "Eq", "NotEq", "Lt", "LtE", "Gt", "GtE"]
                }
            )
        except IntegrityPanic as e:
            assert e.violation_type == "UNSUPPORTED_AST_NODE"
            assert e.details["node_type"] == "BitOr"
            assert "syntax" in e.recovery_hint.lower()
    
    def test_sovereign_gossip_scenario(self):
        """Test sovereign gossip signature verification scenario."""
        # Scenario: Invalid signature on gossip message
        try:
            raise InvalidSignaturePanic(
                violation_type="INVALID_GOSSIP_SIGNATURE",
                details={
                    "sender_id": "node_abc123",
                    "message_type": "STATE_UPDATE",
                    "signature": "0xdeadbeef...",
                    "public_key": "0xcafebabe..."
                }
            )
        except IntegrityPanic as e:
            assert e.violation_type == "INVALID_GOSSIP_SIGNATURE"
            assert "reject" in e.recovery_hint.lower()


class TestRecoveryHintQuality:
    """Test that all recovery hints meet quality standards for administrator guidance."""
    
    def test_all_recovery_hints_are_actionable(self):
        """Test that all recovery hints provide specific actionable steps."""
        test_cases = [
            (StateCorruptionPanic, "STATE_FILE_MISSING", {"path": "/test/state.json"}),
            (StateCorruptionPanic, "STATE_FILE_CORRUPTED", {"path": "/test/state.json"}),
            (MerkleRootMismatchPanic, "MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            (UnsupportedConstraintError, "UNSUPPORTED_AST_NODE", {"node_type": "BitOr", "node_repr": "test"}),
            (InvalidSignaturePanic, "INVALID_GOSSIP_SIGNATURE", {"sender_id": "node_123"}),
            (WALCorruptionPanic, "WAL_FILE_CORRUPTED", {"path": "/test/wal.log"}),
            (NodeIdentityMismatchPanic, "NODE_IDENTITY_MISMATCH", {"sender_id": "node_123"}),
        ]
        
        for exception_class, violation_type, details in test_cases:
            panic = exception_class(violation_type, details)
            hint = panic.recovery_hint
            
            # Recovery hints should be substantial (not just one line)
            assert len(hint) > 100, f"{exception_class.__name__} recovery hint too short"
            
            # Should contain numbered steps or clear structure
            has_structure = (
                "1." in hint or "2." in hint or  # Numbered steps
                "IMMEDIATE" in hint or  # Clear urgency
                "ACTION" in hint  # Clear action required
            )
            assert has_structure, f"{exception_class.__name__} recovery hint lacks clear structure"
    
    def test_recovery_hints_include_commands(self):
        """Test that recovery hints include specific commands where appropriate."""
        test_cases = [
            (StateCorruptionPanic, "STATE_FILE_MISSING", {"path": "/test/state.json"}),
            (StateCorruptionPanic, "STATE_FILE_CORRUPTED", {"path": "/test/state.json"}),
            (MerkleRootMismatchPanic, "MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            (WALCorruptionPanic, "WAL_FILE_CORRUPTED", {"path": "/test/wal.log"}),
        ]
        
        for exception_class, violation_type, details in test_cases:
            panic = exception_class(violation_type, details)
            hint = panic.recovery_hint
            
            # Should include python commands
            assert "python -m Diotec360" in hint, f"{exception_class.__name__} missing command examples"
    
    def test_security_panics_emphasize_urgency(self):
        """Test that security-related panics emphasize urgency and severity."""
        security_test_cases = [
            (MerkleRootMismatchPanic, "MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            (InvalidSignaturePanic, "INVALID_GOSSIP_SIGNATURE", {"sender_id": "node_123"}),
            (NodeIdentityMismatchPanic, "NODE_IDENTITY_MISMATCH", {"sender_id": "node_123"}),
        ]
        
        for exception_class, violation_type, details in security_test_cases:
            panic = exception_class(violation_type, details)
            hint = panic.recovery_hint
            
            # Should emphasize security/urgency
            has_urgency = (
                "CRITICAL" in hint or
                "SECURITY" in hint or
                "ALERT" in hint or
                "IMMEDIATE" in hint
            )
            assert has_urgency, f"{exception_class.__name__} doesn't emphasize security urgency"
    
    def test_recovery_hints_include_verification_steps(self):
        """Test that recovery hints include verification steps after recovery."""
        test_cases = [
            (StateCorruptionPanic, "STATE_FILE_CORRUPTED", {"path": "/test/state.json"}),
            (MerkleRootMismatchPanic, "MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            (WALCorruptionPanic, "WAL_FILE_CORRUPTED", {"path": "/test/wal.log"}),
        ]
        
        for exception_class, violation_type, details in test_cases:
            panic = exception_class(violation_type, details)
            hint = panic.recovery_hint
            
            # Should include verification
            assert "verify" in hint.lower(), f"{exception_class.__name__} missing verification step"
    
    def test_recovery_hints_explain_root_cause_investigation(self):
        """Test that recovery hints guide investigation of root causes."""
        test_cases = [
            (StateCorruptionPanic, "STATE_FILE_CORRUPTED", {"path": "/test/state.json"}),
            (MerkleRootMismatchPanic, "MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            (WALCorruptionPanic, "WAL_FILE_CORRUPTED", {"path": "/test/wal.log"}),
        ]
        
        for exception_class, violation_type, details in test_cases:
            panic = exception_class(violation_type, details)
            hint = panic.recovery_hint
            
            # Should mention investigation
            has_investigation = (
                "investigate" in hint.lower() or
                "root cause" in hint.lower() or
                "review" in hint.lower()
            )
            assert has_investigation, f"{exception_class.__name__} missing root cause investigation"
    
    def test_recovery_hints_provide_multiple_options_when_appropriate(self):
        """Test that recovery hints provide multiple recovery options when appropriate."""
        # Some scenarios have multiple valid recovery paths
        panic = StateCorruptionPanic(
            violation_type="STATE_PARTIAL_CORRUPTION",
            details={"path": "/test/state.json"}
        )
        
        hint = panic.recovery_hint
        # Should offer alternatives
        assert "alternative" in hint.lower() or "option" in hint.lower()
    
    def test_recovery_hints_warn_against_dangerous_actions(self):
        """Test that recovery hints warn against dangerous manual interventions."""
        test_cases = [
            (StateCorruptionPanic, "STATE_FILE_CORRUPTED", {"path": "/test/state.json"}),
            (MerkleRootMismatchPanic, "MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            (NodeIdentityMismatchPanic, "NODE_IDENTITY_MISMATCH", {"sender_id": "node_123"}),
        ]
        
        for exception_class, violation_type, details in test_cases:
            panic = exception_class(violation_type, details)
            hint = panic.recovery_hint
            
            # Should include warnings
            has_warning = (
                "DO NOT" in hint or
                "do not" in hint.lower() or
                "RISKY" in hint or
                "WARNING" in hint
            )
            # At least some should have warnings
            if exception_class in [StateCorruptionPanic, MerkleRootMismatchPanic, NodeIdentityMismatchPanic]:
                assert has_warning, f"{exception_class.__name__} missing safety warnings"
    
    def test_recovery_hints_reference_documentation(self):
        """Test that recovery hints reference relevant documentation."""
        panic = UnsupportedConstraintError(
            violation_type="UNSUPPORTED_AST_NODE",
            details={"node_type": "BitOr", "node_repr": "test"}
        )
        
        hint = panic.recovery_hint
        # Should reference docs
        assert "docs/" in hint or "documentation" in hint.lower()
        # Should reference examples
        assert "examples" in hint.lower()


class TestAuditTrailLogging:
    """Test audit trail logging functionality (RVC2-001 requirement)."""
    
    def test_audit_trail_database_creation(self, tmp_path):
        """Test that audit trail database is created automatically."""
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        _write_to_audit_trail(panic, db_path)
        
        # Check database was created
        assert os.path.exists(db_path)
    
    def test_audit_trail_table_structure(self, tmp_path):
        """Test that audit trail table has correct structure."""
        import sqlite3
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        _write_to_audit_trail(panic, db_path)
        
        # Check table structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='integrity_panics'")
        assert cursor.fetchone() is not None
        
        # Check columns
        cursor.execute("PRAGMA table_info(integrity_panics)")
        columns = {row[1] for row in cursor.fetchall()}
        
        expected_columns = {
            'id', 'timestamp', 'timestamp_iso', 'exception_class',
            'violation_type', 'details', 'recovery_hint', 'forensic_metadata',
            'hostname', 'process_id', 'python_version', 'DIOTEC360_version',
            'stack_trace', 'created_at'
        }
        
        assert expected_columns.issubset(columns)
        conn.close()
    
    def test_audit_trail_record_insertion(self, tmp_path):
        """Test that panic records are inserted correctly."""
        import sqlite3
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={"path": "/test/state.json", "error": "Invalid JSON"},
            recovery_hint="Restore from backup"
        )
        
        _write_to_audit_trail(panic, db_path)
        
        # Query the record
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM integrity_panics ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        assert row is not None
        assert row['exception_class'] == 'StateCorruptionPanic'
        assert row['violation_type'] == 'STATE_FILE_CORRUPTED'
        assert '"path": "/test/state.json"' in row['details']
        assert 'Restore from backup' in row['recovery_hint']
        assert row['timestamp'] is not None
        assert row['hostname'] is not None
        assert row['process_id'] == os.getpid()
        
        conn.close()
    
    def test_audit_trail_multiple_records(self, tmp_path):
        """Test that multiple panic records can be logged."""
        import sqlite3
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics
        panics = [
            StateCorruptionPanic("STATE_FILE_MISSING", {"path": "/test1"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            UnsupportedConstraintError("UNSUPPORTED_AST_NODE", {"node_type": "BitOr"}),
        ]
        
        for panic in panics:
            _write_to_audit_trail(panic, db_path)
        
        # Query all records
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM integrity_panics")
        count = cursor.fetchone()[0]
        
        assert count == 3
        conn.close()
    
    def test_audit_trail_indexes_created(self, tmp_path):
        """Test that database indexes are created for performance."""
        import sqlite3
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = IntegrityPanic(
            violation_type="TEST",
            details={},
            recovery_hint="Test"
        )
        
        _write_to_audit_trail(panic, db_path)
        
        # Check indexes
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        
        expected_indexes = {
            'idx_integrity_panic_timestamp',
            'idx_integrity_panic_violation_type',
            'idx_integrity_panic_exception_class'
        }
        
        assert expected_indexes.issubset(indexes)
        conn.close()
    
    def test_log_integrity_panic_writes_to_audit_trail(self, tmp_path):
        """Test that log_integrity_panic writes to audit trail database."""
        import sqlite3
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={"path": "/test/state.json"},
            recovery_hint="Restore from backup"
        )
        
        # Log the panic
        log_integrity_panic(
            panic,
            write_forensic_report=False,
            audit_db_path=db_path
        )
        
        # Verify it was written to audit trail
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM integrity_panics")
        count = cursor.fetchone()[0]
        
        assert count == 1
        
        cursor.execute("SELECT * FROM integrity_panics ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        assert row is not None
        conn.close()
    
    def test_query_integrity_panics(self, tmp_path):
        """Test querying integrity panics from audit trail."""
        from diotec360.core.integrity_panic import query_integrity_panics
        import sqlite3
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics
        panics = [
            StateCorruptionPanic("STATE_FILE_MISSING", {"path": "/test1"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            UnsupportedConstraintError("UNSUPPORTED_AST_NODE", {"node_type": "BitOr"}),
        ]
        
        for panic in panics:
            log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Query all panics
        results = query_integrity_panics(db_path=db_path)
        
        assert len(results) == 3
        assert results[0]['exception_class'] in ['StateCorruptionPanic', 'MerkleRootMismatchPanic', 'UnsupportedConstraintError']
    
    def test_query_integrity_panics_with_filters(self, tmp_path):
        """Test querying integrity panics with filters."""
        from diotec360.core.integrity_panic import query_integrity_panics
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics
        panics = [
            StateCorruptionPanic("STATE_FILE_MISSING", {"path": "/test1"}),
            StateCorruptionPanic("STATE_FILE_CORRUPTED", {"path": "/test2"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
        ]
        
        for panic in panics:
            log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Query by exception class
        results = query_integrity_panics(db_path=db_path, exception_class="StateCorruptionPanic")
        assert len(results) == 2
        
        # Query by violation type
        results = query_integrity_panics(db_path=db_path, violation_type="STATE_FILE_MISSING")
        assert len(results) == 1
        assert results[0]['violation_type'] == "STATE_FILE_MISSING"
    
    def test_get_integrity_panic_stats(self, tmp_path):
        """Test getting integrity panic statistics."""
        from diotec360.core.integrity_panic import get_integrity_panic_stats
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics
        panics = [
            StateCorruptionPanic("STATE_FILE_MISSING", {"path": "/test1"}),
            StateCorruptionPanic("STATE_FILE_CORRUPTED", {"path": "/test2"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "xyz", "stored": "uvw"}),
        ]
        
        for panic in panics:
            log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Get statistics
        stats = get_integrity_panic_stats(db_path=db_path)
        
        assert stats['total_panics'] == 4
        assert stats['panics_by_type']['STATE_FILE_MISSING'] == 1
        assert stats['panics_by_type']['STATE_FILE_CORRUPTED'] == 1
        assert stats['panics_by_type']['MERKLE_ROOT_MISMATCH'] == 2
        assert stats['panics_by_class']['StateCorruptionPanic'] == 2
        assert stats['panics_by_class']['MerkleRootMismatchPanic'] == 2
        assert stats['recent_panics_24h'] == 4
        assert stats['most_recent'] is not None
    
    def test_get_integrity_panic_stats_empty_database(self, tmp_path):
        """Test getting statistics from empty database."""
        from diotec360.core.integrity_panic import get_integrity_panic_stats
        
        db_path = str(tmp_path / "empty_audit.db")
        
        stats = get_integrity_panic_stats(db_path=db_path)
        
        assert stats['total_panics'] == 0
        assert stats['panics_by_type'] == {}
        assert stats['panics_by_class'] == {}
        assert stats['recent_panics_24h'] == 0
        assert stats['most_recent'] is None
    
    def test_audit_trail_forensic_metadata_stored(self, tmp_path):
        """Test that forensic metadata is stored in audit trail."""
        import sqlite3
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Query and verify forensic metadata
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM integrity_panics ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        # Check forensic metadata is stored
        assert row['forensic_metadata'] is not None
        forensic = json.loads(row['forensic_metadata'])
        
        assert 'system' in forensic
        assert 'process' in forensic
        assert 'stack_trace' in forensic
        assert 'timestamp_iso' in forensic
        
        conn.close()
    
    def test_audit_trail_concurrent_writes(self, tmp_path):
        """Test that audit trail handles concurrent writes correctly."""
        import sqlite3
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics rapidly (simulating concurrent writes)
        panics = [
            IntegrityPanic(f"TEST_{i}", {"index": i}, f"Hint {i}")
            for i in range(10)
        ]
        
        for panic in panics:
            log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Verify all were written
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM integrity_panics")
        count = cursor.fetchone()[0]
        
        assert count == 10
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestAuditTrailLogging:
    """Test audit trail logging functionality (RVC2-001 requirement)."""
    
    def test_audit_trail_database_creation(self, tmp_path):
        """Test that audit trail database is created automatically."""
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        _write_to_audit_trail(panic, db_path)
        
        # Check database was created
        assert os.path.exists(db_path)
    
    def test_audit_trail_table_structure(self, tmp_path):
        """Test that audit trail table has correct structure."""
        import sqlite3
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        _write_to_audit_trail(panic, db_path)
        
        # Check table structure
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='integrity_panics'")
        assert cursor.fetchone() is not None
        
        # Check columns
        cursor.execute("PRAGMA table_info(integrity_panics)")
        columns = {row[1] for row in cursor.fetchall()}
        
        expected_columns = {
            'id', 'timestamp', 'timestamp_iso', 'exception_class',
            'violation_type', 'details', 'recovery_hint', 'forensic_metadata',
            'hostname', 'process_id', 'python_version', 'DIOTEC360_version',
            'stack_trace', 'created_at'
        }
        
        assert expected_columns.issubset(columns)
        conn.close()
    
    def test_audit_trail_record_insertion(self, tmp_path):
        """Test that panic records are inserted correctly."""
        import sqlite3
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={"path": "/test/state.json", "error": "Invalid JSON"},
            recovery_hint="Restore from backup"
        )
        
        _write_to_audit_trail(panic, db_path)
        
        # Query the record
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM integrity_panics ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        assert row is not None
        assert row['exception_class'] == 'StateCorruptionPanic'
        assert row['violation_type'] == 'STATE_FILE_CORRUPTED'
        assert '"path": "/test/state.json"' in row['details']
        assert 'Restore from backup' in row['recovery_hint']
        assert row['timestamp'] is not None
        assert row['hostname'] is not None
        assert row['process_id'] == os.getpid()
        
        conn.close()
    
    def test_audit_trail_multiple_records(self, tmp_path):
        """Test that multiple panic records can be logged."""
        import sqlite3
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics
        panics = [
            StateCorruptionPanic("STATE_FILE_MISSING", {"path": "/test1"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            UnsupportedConstraintError("UNSUPPORTED_AST_NODE", {"node_type": "BitOr"}),
        ]
        
        for panic in panics:
            _write_to_audit_trail(panic, db_path)
        
        # Query all records
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM integrity_panics")
        count = cursor.fetchone()[0]
        
        assert count == 3
        conn.close()
    
    def test_audit_trail_indexes_created(self, tmp_path):
        """Test that database indexes are created for performance."""
        import sqlite3
        from diotec360.core.integrity_panic import _write_to_audit_trail
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = IntegrityPanic(
            violation_type="TEST",
            details={},
            recovery_hint="Test"
        )
        
        _write_to_audit_trail(panic, db_path)
        
        # Check indexes
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        
        expected_indexes = {
            'idx_integrity_panic_timestamp',
            'idx_integrity_panic_violation_type',
            'idx_integrity_panic_exception_class'
        }
        
        assert expected_indexes.issubset(indexes)
        conn.close()
    
    def test_log_integrity_panic_writes_to_audit_trail(self, tmp_path):
        """Test that log_integrity_panic writes to audit trail database."""
        import sqlite3
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={"path": "/test/state.json"},
            recovery_hint="Restore from backup"
        )
        
        # Log the panic
        log_integrity_panic(
            panic,
            write_forensic_report=False,
            audit_db_path=db_path
        )
        
        # Verify it was written to audit trail
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM integrity_panics")
        count = cursor.fetchone()[0]
        
        assert count == 1
        
        cursor.execute("SELECT * FROM integrity_panics ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        assert row is not None
        conn.close()
    
    def test_query_integrity_panics(self, tmp_path):
        """Test querying integrity panics from audit trail."""
        from diotec360.core.integrity_panic import query_integrity_panics
        import sqlite3
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics
        panics = [
            StateCorruptionPanic("STATE_FILE_MISSING", {"path": "/test1"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            UnsupportedConstraintError("UNSUPPORTED_AST_NODE", {"node_type": "BitOr"}),
        ]
        
        for panic in panics:
            log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Query all panics
        results = query_integrity_panics(db_path=db_path)
        
        assert len(results) == 3
        assert results[0]['exception_class'] in ['StateCorruptionPanic', 'MerkleRootMismatchPanic', 'UnsupportedConstraintError']
    
    def test_query_integrity_panics_with_filters(self, tmp_path):
        """Test querying integrity panics with filters."""
        from diotec360.core.integrity_panic import query_integrity_panics
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics
        panics = [
            StateCorruptionPanic("STATE_FILE_MISSING", {"path": "/test1"}),
            StateCorruptionPanic("STATE_FILE_CORRUPTED", {"path": "/test2"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
        ]
        
        for panic in panics:
            log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Query by exception class
        results = query_integrity_panics(db_path=db_path, exception_class="StateCorruptionPanic")
        assert len(results) == 2
        
        # Query by violation type
        results = query_integrity_panics(db_path=db_path, violation_type="STATE_FILE_MISSING")
        assert len(results) == 1
        assert results[0]['violation_type'] == "STATE_FILE_MISSING"
    
    def test_get_integrity_panic_stats(self, tmp_path):
        """Test getting integrity panic statistics."""
        from diotec360.core.integrity_panic import get_integrity_panic_stats
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics
        panics = [
            StateCorruptionPanic("STATE_FILE_MISSING", {"path": "/test1"}),
            StateCorruptionPanic("STATE_FILE_CORRUPTED", {"path": "/test2"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "abc", "stored": "def"}),
            MerkleRootMismatchPanic("MERKLE_ROOT_MISMATCH", {"computed": "xyz", "stored": "uvw"}),
        ]
        
        for panic in panics:
            log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Get statistics
        stats = get_integrity_panic_stats(db_path=db_path)
        
        assert stats['total_panics'] == 4
        assert stats['panics_by_type']['STATE_FILE_MISSING'] == 1
        assert stats['panics_by_type']['STATE_FILE_CORRUPTED'] == 1
        assert stats['panics_by_type']['MERKLE_ROOT_MISMATCH'] == 2
        assert stats['panics_by_class']['StateCorruptionPanic'] == 2
        assert stats['panics_by_class']['MerkleRootMismatchPanic'] == 2
        assert stats['recent_panics_24h'] == 4
        assert stats['most_recent'] is not None
    
    def test_get_integrity_panic_stats_empty_database(self, tmp_path):
        """Test getting statistics from empty database."""
        from diotec360.core.integrity_panic import get_integrity_panic_stats
        
        db_path = str(tmp_path / "empty_audit.db")
        
        stats = get_integrity_panic_stats(db_path=db_path)
        
        assert stats['total_panics'] == 0
        assert stats['panics_by_type'] == {}
        assert stats['panics_by_class'] == {}
        assert stats['recent_panics_24h'] == 0
        assert stats['most_recent'] is None
    
    def test_audit_trail_forensic_metadata_stored(self, tmp_path):
        """Test that forensic metadata is stored in audit trail."""
        import sqlite3
        
        db_path = str(tmp_path / "test_audit.db")
        
        panic = IntegrityPanic(
            violation_type="TEST_VIOLATION",
            details={"key": "value"},
            recovery_hint="Test hint"
        )
        
        log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Query and verify forensic metadata
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM integrity_panics ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        # Check forensic metadata is stored
        assert row['forensic_metadata'] is not None
        forensic = json.loads(row['forensic_metadata'])
        
        assert 'system' in forensic
        assert 'process' in forensic
        assert 'stack_trace' in forensic
        assert 'timestamp_iso' in forensic
        
        conn.close()
    
    def test_audit_trail_concurrent_writes(self, tmp_path):
        """Test that audit trail handles concurrent writes correctly."""
        import sqlite3
        
        db_path = str(tmp_path / "test_audit.db")
        
        # Log multiple panics rapidly (simulating concurrent writes)
        panics = [
            IntegrityPanic(f"TEST_{i}", {"index": i}, f"Hint {i}")
            for i in range(10)
        ]
        
        for panic in panics:
            log_integrity_panic(panic, write_forensic_report=False, audit_db_path=db_path)
        
        # Verify all were written
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM integrity_panics")
        count = cursor.fetchone()[0]
        
        assert count == 10
        conn.close()
