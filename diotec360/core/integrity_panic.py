"""
IntegrityPanic Exception Framework

Centralized exception handling for all integrity violations in Aethel v1.9.2.
Implements zero-tolerance integrity enforcement with fail-closed behavior.

Design Philosophy: "Better to stop than to lie"
"""

import time
import json
import os
import sys
import traceback
import platform
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List


class IntegrityPanic(Exception):
    """
    Base exception for all integrity violations.
    
    All integrity violations in Aethel trigger this exception or its subclasses,
    forcing the system to halt rather than continue with corrupted or unverified data.
    
    Attributes:
        violation_type: Classification of the integrity violation
        details: Diagnostic information about the violation
        recovery_hint: Human-readable guidance for recovery
        timestamp: When the violation was detected
    """
    
    def __init__(
        self,
        violation_type: str,
        details: Dict[str, Any],
        recovery_hint: str
    ):
        """
        Initialize an IntegrityPanic exception.
        
        Args:
            violation_type: Type of integrity violation (e.g., "STATE_FILE_CORRUPTED")
            details: Dictionary containing diagnostic information
            recovery_hint: Human-readable recovery instructions
        """
        self.violation_type = violation_type
        self.details = details
        self.recovery_hint = recovery_hint
        self.timestamp = time.time()
        
        # Capture forensic metadata
        self.forensic_metadata = self._capture_forensic_metadata()
        
        # Format error message
        message = self._format_message()
        super().__init__(message)
    
    def _capture_forensic_metadata(self) -> Dict[str, Any]:
        """
        Capture comprehensive forensic metadata for investigation.
        
        Returns:
            Dictionary containing system context, stack trace, and environment info
        """
        metadata = {
            # Timestamp information
            "timestamp_iso": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(self.timestamp)),
            "timestamp_unix": self.timestamp,
            
            # System information
            "system": {
                "hostname": platform.node(),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.machine(),
            },
            
            # Process information
            "process": {
                "pid": os.getpid(),
                "cwd": os.getcwd(),
                "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
            },
            
            # Stack trace for debugging
            "stack_trace": self._capture_stack_trace(),
            
            # Environment context
            "environment": {
                "aethel_version": self._get_aethel_version(),
                "python_path": sys.executable,
            }
        }
        
        return metadata
    
    def _capture_stack_trace(self) -> list:
        """
        Capture the current stack trace for forensic analysis.
        
        Returns:
            List of stack frame information
        """
        # Get the stack trace, excluding this method and __init__
        stack = traceback.extract_stack()[:-2]
        
        return [
            {
                "filename": frame.filename,
                "line": frame.lineno,
                "function": frame.name,
                "code": frame.line
            }
            for frame in stack
        ]
    
    def _get_aethel_version(self) -> str:
        """
        Get the Aethel version if available.
        
        Returns:
            Version string or "unknown"
        """
        try:
            # Try to import version from aethel package
            from aethel import __version__
            return __version__
        except (ImportError, AttributeError):
            return "1.9.2"  # Default to current version
    
    def _format_message(self) -> str:
        """Format a comprehensive error message."""
        lines = [
            f"🚨 INTEGRITY PANIC: {self.violation_type}",
            f"",
            f"Details:",
        ]
        
        for key, value in self.details.items():
            lines.append(f"  {key}: {value}")
        
        lines.extend([
            f"",
            f"Recovery Hint:",
            f"  {self.recovery_hint}",
            f"",
            f"Timestamp: {self.timestamp}",
        ])
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize exception to dictionary for logging/audit.
        
        Returns:
            Dictionary representation of the exception with full forensic metadata
        """
        return {
            "exception_class": self.__class__.__name__,
            "violation_type": self.violation_type,
            "details": self.details,
            "recovery_hint": self.recovery_hint,
            "timestamp": self.timestamp,
            "forensic_metadata": self.forensic_metadata,
        }
    
    def to_json(self) -> str:
        """
        Serialize exception to JSON for logging/audit.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    def write_forensic_report(self, output_dir: str = ".") -> str:
        """
        Write a comprehensive forensic report to disk.
        
        Args:
            output_dir: Directory to write the report (default: current directory)
        
        Returns:
            Path to the written report file
        """
        # Create filename with timestamp and violation type
        timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.gmtime(self.timestamp))
        filename = f"integrity_panic_{self.violation_type}_{timestamp_str}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Write report
        with open(filepath, 'w') as f:
            f.write(self.to_json())
        
        return filepath


class StateCorruptionPanic(IntegrityPanic):
    """
    State file is corrupted or unreadable.
    
    Raised when:
    - state.json file is missing
    - state.json contains invalid JSON
    - state.json is partially corrupted
    - File system errors prevent reading state
    
    Recovery:
    - Restore from Genesis Vault backup
    - Initialize new genesis state if appropriate
    """
    
    # Recovery hint templates for different scenarios
    RECOVERY_HINTS = {
        "STATE_FILE_MISSING": (
            "IMMEDIATE ACTION REQUIRED:\n"
            "1. Check if state.json was accidentally deleted or moved\n"
            "2. Restore from Genesis Vault backup:\n"
            "   - Locate latest backup in .aethel_vault/\n"
            "   - Run: python -m aethel.genesis.restore --backup <backup_id>\n"
            "3. If no backup exists and this is a new installation:\n"
            "   - Run: python -m aethel.genesis.init\n"
            "4. Verify restored state integrity before resuming operations\n"
            "5. Review system logs to determine cause of file loss"
        ),
        "STATE_FILE_CORRUPTED": (
            "IMMEDIATE ACTION REQUIRED:\n"
            "1. DO NOT attempt to manually edit the corrupted file\n"
            "2. Preserve corrupted file for forensic analysis:\n"
            "   - Run: cp state.json state.json.corrupted.$(date +%s)\n"
            "3. Restore from Genesis Vault backup:\n"
            "   - List available backups: python -m aethel.genesis.list_backups\n"
            "   - Restore latest: python -m aethel.genesis.restore --latest\n"
            "4. Verify Merkle Root after restoration\n"
            "5. Investigate root cause (disk failure, power loss, etc.)\n"
            "6. Consider enabling automatic backup verification"
        ),
        "STATE_PARTIAL_CORRUPTION": (
            "IMMEDIATE ACTION REQUIRED:\n"
            "1. System detected partial state corruption\n"
            "2. Restore from Genesis Vault backup (safest option):\n"
            "   - Run: python -m aethel.genesis.restore --verify\n"
            "3. Alternative: Attempt state reconstruction (RISKY):\n"
            "   - Run: python -m aethel.tools.reconstruct_state --from-wal\n"
            "   - This will replay WAL transactions from last checkpoint\n"
            "4. After recovery, run full integrity check:\n"
            "   - Run: python -m aethel.tools.verify_state --full\n"
            "5. Review system health and consider hardware diagnostics"
        ),
    }
    
    def __init__(
        self,
        violation_type: str,
        details: Dict[str, Any],
        recovery_hint: Optional[str] = None
    ):
        # Use template if no custom hint provided
        if recovery_hint is None:
            recovery_hint = self.RECOVERY_HINTS.get(
                violation_type,
                "Restore from Genesis Vault backup or initialize new genesis state"
            )
        super().__init__(violation_type, details, recovery_hint)


class MerkleRootMismatchPanic(IntegrityPanic):
    """
    Merkle root doesn't match computed value.
    
    Raised when:
    - Stored Merkle root differs from computed root
    - State has been tampered with
    - Integrity verification fails
    
    Recovery:
    - Restore from verified backup
    - Investigate potential security breach
    """
    
    # Recovery hint templates
    RECOVERY_HINTS = {
        "MERKLE_ROOT_MISMATCH": (
            "CRITICAL SECURITY ALERT - IMMEDIATE ACTION REQUIRED:\n"
            "1. HALT all operations immediately - state integrity compromised\n"
            "2. Preserve current state for forensic investigation:\n"
            "   - Run: python -m aethel.forensics.capture_state --output forensics/\n"
            "3. DO NOT trust current state - potential tampering detected\n"
            "4. Restore from last verified backup:\n"
            "   - List verified backups: python -m aethel.genesis.list_backups --verified-only\n"
            "   - Restore: python -m aethel.genesis.restore --backup <backup_id> --verify-merkle\n"
            "5. Investigate security breach:\n"
            "   - Check system logs for unauthorized access\n"
            "   - Review file system permissions\n"
            "   - Scan for malware/rootkits\n"
            "   - Audit recent administrative actions\n"
            "6. After restoration, verify Merkle Root:\n"
            "   - Run: python -m aethel.tools.verify_merkle --full\n"
            "7. Consider rotating cryptographic keys\n"
            "8. Enable enhanced monitoring and alerting"
        ),
        "MERKLE_ROOT_MISSING": (
            "IMMEDIATE ACTION REQUIRED:\n"
            "1. State file exists but Merkle Root is missing\n"
            "2. This may indicate incomplete state write or old format\n"
            "3. Restore from Genesis Vault backup (recommended):\n"
            "   - Run: python -m aethel.genesis.restore --latest --verify\n"
            "4. Alternative: Recompute Merkle Root (if state is trusted):\n"
            "   - Run: python -m aethel.tools.recompute_merkle --verify\n"
            "5. Verify state integrity after recovery\n"
            "6. Update to latest Aethel version if using old format"
        ),
    }
    
    def __init__(
        self,
        violation_type: str,
        details: Dict[str, Any],
        recovery_hint: Optional[str] = None
    ):
        if recovery_hint is None:
            recovery_hint = self.RECOVERY_HINTS.get(
                violation_type,
                "State has been tampered with. Restore from verified backup and investigate security breach."
            )
        super().__init__(violation_type, details, recovery_hint)


class UnsupportedConstraintError(IntegrityPanic):
    """
    Constraint cannot be verified by Z3 solver.
    
    Raised when:
    - AST node type not in supported whitelist
    - Constraint uses unsupported syntax
    - Security constraint cannot be verified
    
    Recovery:
    - Rewrite constraint using supported syntax
    - Consult documentation for supported operations
    - Transaction must be rejected
    """
    
    # Recovery hint templates
    RECOVERY_HINTS = {
        "UNSUPPORTED_AST_NODE": (
            "TRANSACTION REJECTED - CONSTRAINT SYNTAX ERROR:\n"
            "1. The constraint uses unsupported syntax that cannot be verified\n"
            "2. Review the constraint in your transaction:\n"
            "   - Unsupported operation: {node_type}\n"
            "   - Location: {node_repr}\n"
            "3. Supported AST node types:\n"
            "   {supported_alternatives}\n"
            "4. Rewrite using supported operations:\n"
            "   - Arithmetic: +, -, *, /, % (Add, Sub, Mult, Div, Mod)\n"
            "   - Comparison: ==, !=, <, <=, >, >= (Eq, NotEq, Lt, LtE, Gt, GtE)\n"
            "   - Unary: -, + (USub, UAdd)\n"
            "   - Variables: balance, amount, sender, receiver (Name)\n"
            "   - Constants: numbers (Constant, Num)\n"
            "5. Consult documentation:\n"
            "   - Read: docs/language-reference/conservation-laws.md\n"
            "   - Examples: aethel/examples/\n"
            "6. Test constraint syntax:\n"
            "   - Run: python -m aethel.tools.validate_constraint '<constraint>'\n"
            "7. Submit corrected transaction\n"
            "\n"
            "SECURITY NOTE: Aethel uses fail-closed verification. If a constraint\n"
            "cannot be verified, the transaction is rejected. This prevents\n"
            "security bypasses through unsupported syntax."
        ),
        "CONSTRAINT_TOO_COMPLEX": (
            "TRANSACTION REJECTED - CONSTRAINT TOO COMPLEX:\n"
            "1. The constraint exceeds complexity limits for Z3 verification\n"
            "2. Simplify your constraint:\n"
            "   - Break into multiple simpler constraints\n"
            "   - Reduce nesting depth\n"
            "   - Eliminate redundant conditions\n"
            "3. Consider using multiple transactions\n"
            "4. Contact support if legitimate use case requires complex constraints"
        ),
    }
    
    def __init__(
        self,
        violation_type: str,
        details: Dict[str, Any],
        recovery_hint: Optional[str] = None
    ):
        if recovery_hint is None:
            # Format hint with details if available
            hint_template = self.RECOVERY_HINTS.get(
                violation_type,
                "Rewrite constraint using supported syntax. See documentation for supported operations."
            )
            try:
                # Format supported_types as a readable list
                if "supported_types" in details:
                    supported_list = details["supported_types"]
                    # Group by category for better readability
                    categories = {
                        "Arithmetic": ["Add", "Sub", "Mult", "Div", "Mod"],
                        "Comparison": ["Eq", "NotEq", "Lt", "LtE", "Gt", "GtE"],
                        "Unary": ["USub", "UAdd"],
                        "Structural": ["BinOp", "UnaryOp", "Compare", "Name", "Constant", "Num"]
                    }
                    
                    formatted_alternatives = []
                    for category, types in categories.items():
                        matching = [t for t in types if t in supported_list]
                        if matching:
                            formatted_alternatives.append(f"     {category}: {', '.join(matching)}")
                    
                    # Add any remaining types not in categories
                    categorized = set(sum(categories.values(), []))
                    remaining = [t for t in supported_list if t not in categorized]
                    if remaining:
                        formatted_alternatives.append(f"     Other: {', '.join(remaining)}")
                    
                    details_with_formatted = details.copy()
                    details_with_formatted["supported_alternatives"] = "\n".join(formatted_alternatives)
                    recovery_hint = hint_template.format(**details_with_formatted)
                else:
                    recovery_hint = hint_template.format(**details)
            except (KeyError, ValueError):
                recovery_hint = hint_template
        super().__init__(violation_type, details, recovery_hint)


class InvalidSignaturePanic(IntegrityPanic):
    """
    Cryptographic signature verification failed.
    
    Raised when:
    - ED25519 signature is invalid
    - Message has been tampered with
    - Sender identity cannot be verified
    - Unsigned message received
    
    Recovery:
    - Reject message from untrusted source
    - Investigate potential security breach
    - Verify sender's public key
    """
    
    # Recovery hint templates
    RECOVERY_HINTS = {
        "INVALID_GOSSIP_SIGNATURE": (
            "SECURITY ALERT - INVALID MESSAGE SIGNATURE:\n"
            "1. Message from node '{sender_id}' has invalid signature\n"
            "2. IMMEDIATE ACTIONS:\n"
            "   - Message has been REJECTED automatically\n"
            "   - Connection to sender may be compromised\n"
            "3. Investigate the source:\n"
            "   - Verify sender's public key: python -m aethel.tools.verify_node_key {sender_id}\n"
            "   - Check if sender's key has been rotated\n"
            "   - Review network logs for suspicious activity\n"
            "4. If sender is legitimate:\n"
            "   - Contact node operator to verify key\n"
            "   - Update node registry if key was rotated\n"
            "   - Re-establish secure connection\n"
            "5. If sender is malicious:\n"
            "   - Blacklist node: python -m aethel.network.blacklist {sender_id}\n"
            "   - Report to network administrators\n"
            "   - Review other messages from this sender\n"
            "6. Enable enhanced signature verification logging\n"
            "7. Consider implementing rate limiting for failed signatures"
        ),
        "UNSIGNED_MESSAGE": (
            "SECURITY ALERT - UNSIGNED MESSAGE RECEIVED:\n"
            "1. Received message without required signature\n"
            "2. Message has been REJECTED automatically\n"
            "3. This may indicate:\n"
            "   - Outdated client software\n"
            "   - Configuration error\n"
            "   - Attempted security bypass\n"
            "4. Actions:\n"
            "   - Verify sender is using Aethel v1.9.2 or later\n"
            "   - Check sender's configuration for signature settings\n"
            "   - If persistent, blacklist sender\n"
            "5. All gossip messages MUST be signed with ED25519"
        ),
        "PUBLIC_KEY_MISMATCH": (
            "SECURITY ALERT - PUBLIC KEY MISMATCH:\n"
            "1. Sender's public key does not match registered key\n"
            "2. This may indicate:\n"
            "   - Key rotation without proper notification\n"
            "   - Impersonation attempt\n"
            "   - Compromised node\n"
            "3. IMMEDIATE ACTIONS:\n"
            "   - Connection REJECTED automatically\n"
            "   - Verify sender identity out-of-band (phone, email, etc.)\n"
            "   - Do NOT accept new key without verification\n"
            "4. If key rotation is legitimate:\n"
            "   - Obtain signed key rotation certificate\n"
            "   - Update node registry: python -m aethel.network.update_key {sender_id}\n"
            "5. If impersonation suspected:\n"
            "   - Alert network administrators immediately\n"
            "   - Blacklist attacker's address\n"
            "   - Review all recent messages from this sender"
        ),
    }
    
    def __init__(
        self,
        violation_type: str,
        details: Dict[str, Any],
        recovery_hint: Optional[str] = None
    ):
        if recovery_hint is None:
            hint_template = self.RECOVERY_HINTS.get(
                violation_type,
                "Reject message from untrusted source. Verify sender identity and investigate potential attack."
            )
            try:
                recovery_hint = hint_template.format(**details)
            except (KeyError, ValueError):
                recovery_hint = hint_template
        super().__init__(violation_type, details, recovery_hint)


class WALCorruptionPanic(IntegrityPanic):
    """
    Write-Ahead Log is corrupted or inconsistent.
    
    Raised when:
    - WAL file is corrupted
    - WAL entries are inconsistent with state
    - Transaction log cannot be replayed
    
    Recovery:
    - Restore from backup
    - Replay transactions from last checkpoint
    """
    
    # Recovery hint templates
    RECOVERY_HINTS = {
        "WAL_FILE_CORRUPTED": (
            "IMMEDIATE ACTION REQUIRED - WAL CORRUPTION DETECTED:\n"
            "1. Write-Ahead Log is corrupted - transaction history compromised\n"
            "2. Preserve corrupted WAL for analysis:\n"
            "   - Run: cp wal.log wal.log.corrupted.$(date +%s)\n"
            "3. Assess damage:\n"
            "   - Run: python -m aethel.tools.analyze_wal --corrupted wal.log.corrupted.*\n"
            "   - Identify last valid transaction\n"
            "4. Recovery options:\n"
            "   Option A (Safest): Restore from backup\n"
            "   - Run: python -m aethel.genesis.restore --latest --verify\n"
            "   \n"
            "   Option B (Partial recovery): Replay from checkpoint\n"
            "   - Run: python -m aethel.tools.replay_wal --from-checkpoint\n"
            "   - This may lose recent transactions\n"
            "5. After recovery:\n"
            "   - Verify state integrity: python -m aethel.tools.verify_state\n"
            "   - Check for missing transactions\n"
            "   - Notify affected users if transactions were lost\n"
            "6. Investigate root cause:\n"
            "   - Check disk health: run SMART diagnostics\n"
            "   - Review system logs for I/O errors\n"
            "   - Consider hardware replacement if disk is failing"
        ),
        "WAL_STATE_INCONSISTENCY": (
            "IMMEDIATE ACTION REQUIRED - WAL/STATE MISMATCH:\n"
            "1. WAL and state.json are inconsistent\n"
            "2. This indicates incomplete transaction commit or crash during write\n"
            "3. DO NOT manually edit files\n"
            "4. Recovery procedure:\n"
            "   - Run: python -m aethel.tools.reconcile_wal_state\n"
            "   - This will analyze and repair inconsistencies\n"
            "5. If reconciliation fails:\n"
            "   - Restore from Genesis Vault backup\n"
            "   - Run: python -m aethel.genesis.restore --verify\n"
            "6. After recovery:\n"
            "   - Verify atomicity: python -m aethel.tools.verify_atomicity\n"
            "   - Enable WAL checksums for future protection"
        ),
        "WAL_REPLAY_FAILED": (
            "IMMEDIATE ACTION REQUIRED - WAL REPLAY FAILURE:\n"
            "1. Cannot replay transactions from WAL\n"
            "2. This may indicate:\n"
            "   - Corrupted transaction data\n"
            "   - Incompatible WAL format\n"
            "   - Missing dependencies\n"
            "3. Recovery:\n"
            "   - Restore from backup (recommended)\n"
            "   - Run: python -m aethel.genesis.restore --latest\n"
            "4. If backup is unavailable:\n"
            "   - Attempt partial replay: python -m aethel.tools.replay_wal --skip-errors\n"
            "   - Review skipped transactions manually\n"
            "5. Update to latest Aethel version if format incompatibility detected"
        ),
    }
    
    def __init__(
        self,
        violation_type: str,
        details: Dict[str, Any],
        recovery_hint: Optional[str] = None
    ):
        if recovery_hint is None:
            recovery_hint = self.RECOVERY_HINTS.get(
                violation_type,
                "WAL corruption detected. Restore from backup and replay transactions from last checkpoint."
            )
        super().__init__(violation_type, details, recovery_hint)


class NodeIdentityMismatchPanic(IntegrityPanic):
    """
    Node identity does not match expected public key.
    
    Raised when:
    - Node's public key changes unexpectedly
    - Potential impersonation attack
    - Identity verification fails
    
    Recovery:
    - Reject connection from suspicious node
    - Verify node's identity out-of-band
    - Investigate potential security breach
    """
    
    # Recovery hint templates
    RECOVERY_HINTS = {
        "NODE_IDENTITY_MISMATCH": (
            "CRITICAL SECURITY ALERT - NODE IMPERSONATION DETECTED:\n"
            "1. Node '{sender_id}' is using a different public key than registered\n"
            "2. IMMEDIATE ACTIONS (AUTOMATIC):\n"
            "   - Connection REJECTED\n"
            "   - All messages from this node BLOCKED\n"
            "   - Security event logged\n"
            "3. This is a CRITICAL security event indicating:\n"
            "   - Possible impersonation attack\n"
            "   - Compromised node\n"
            "   - Man-in-the-middle attack\n"
            "4. REQUIRED ACTIONS:\n"
            "   - DO NOT accept connection without verification\n"
            "   - Contact node operator via secure out-of-band channel:\n"
            "     * Phone call (verify caller ID)\n"
            "     * In-person verification\n"
            "     * Signed email with known PGP key\n"
            "   - Verify if key rotation was intentional\n"
            "5. If key rotation is legitimate:\n"
            "   - Obtain signed key rotation certificate\n"
            "   - Verify certificate signature\n"
            "   - Update node registry: python -m aethel.network.update_node_key {sender_id} --cert <cert_file>\n"
            "   - Re-establish connection\n"
            "6. If impersonation attack confirmed:\n"
            "   - Permanently blacklist attacker: python -m aethel.network.blacklist {sender_id} --permanent\n"
            "   - Alert all network participants\n"
            "   - Report to security team\n"
            "   - Review all recent activity from this node\n"
            "   - Check for data exfiltration\n"
            "7. Enhance security:\n"
            "   - Enable key pinning for critical nodes\n"
            "   - Implement certificate transparency\n"
            "   - Review network access controls"
        ),
        "NODE_KEY_ROTATION_UNVERIFIED": (
            "SECURITY ALERT - UNVERIFIED KEY ROTATION:\n"
            "1. Node '{sender_id}' presented new key without proper certificate\n"
            "2. Connection REJECTED pending verification\n"
            "3. Required actions:\n"
            "   - Request signed key rotation certificate from node operator\n"
            "   - Verify certificate: python -m aethel.tools.verify_key_rotation_cert <cert_file>\n"
            "   - If valid, update registry: python -m aethel.network.accept_key_rotation {sender_id}\n"
            "4. Do NOT accept key rotation without proper verification"
        ),
    }
    
    def __init__(
        self,
        violation_type: str,
        details: Dict[str, Any],
        recovery_hint: Optional[str] = None
    ):
        if recovery_hint is None:
            hint_template = self.RECOVERY_HINTS.get(
                violation_type,
                "Node identity mismatch detected. Possible impersonation attack. Verify node identity and reject connection."
            )
            try:
                recovery_hint = hint_template.format(**details)
            except (KeyError, ValueError):
                recovery_hint = hint_template
        super().__init__(violation_type, details, recovery_hint)


# Convenience function for logging integrity panics
def log_integrity_panic(
    panic: IntegrityPanic,
    logger=None,
    write_forensic_report: bool = True,
    forensic_dir: str = ".aethel_state",
    audit_db_path: str = ".aethel_sentinel/telemetry.db"
) -> Optional[str]:
    """
    Log an IntegrityPanic to the audit trail and optionally write forensic report.
    
    This function implements the "Exceptions logged to audit trail" requirement
    by persisting all IntegrityPanic events to the telemetry database for
    forensic analysis and compliance auditing.
    
    Args:
        panic: The IntegrityPanic exception to log
        logger: Optional logger instance (uses print if None)
        write_forensic_report: Whether to write a forensic report to disk
        forensic_dir: Directory for forensic reports
        audit_db_path: Path to the audit/telemetry database
    
    Returns:
        Path to forensic report if written, None otherwise
    """
    # Log to console/logger
    if logger:
        logger.critical(f"INTEGRITY_PANIC: {panic.to_json()}")
    else:
        print(f"🚨 INTEGRITY PANIC LOGGED:\n{panic.to_json()}")
    
    # Write to audit trail database
    try:
        _write_to_audit_trail(panic, audit_db_path)
        if logger:
            logger.info(f"IntegrityPanic logged to audit trail: {audit_db_path}")
        else:
            print(f"📊 Audit trail updated: {audit_db_path}")
    except Exception as e:
        if logger:
            logger.error(f"Failed to write to audit trail: {e}")
        else:
            print(f"⚠️  Failed to write to audit trail: {e}")
    
    # Write forensic report if requested
    forensic_path = None
    if write_forensic_report:
        try:
            forensic_path = panic.write_forensic_report(forensic_dir)
            if logger:
                logger.info(f"Forensic report written to: {forensic_path}")
            else:
                print(f"📋 Forensic report written to: {forensic_path}")
        except Exception as e:
            if logger:
                logger.error(f"Failed to write forensic report: {e}")
            else:
                print(f"⚠️  Failed to write forensic report: {e}")
    
    return forensic_path


def _write_to_audit_trail(panic: IntegrityPanic, db_path: str):
    """
    Write IntegrityPanic to the audit trail database.
    
    This creates a persistent record of all integrity violations for:
    - Forensic investigation
    - Compliance auditing
    - Security monitoring
    - Incident response
    
    Args:
        panic: The IntegrityPanic exception to log
        db_path: Path to the telemetry/audit database
    """
    # Ensure database directory exists
    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create integrity_panics table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS integrity_panics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            timestamp_iso TEXT NOT NULL,
            exception_class TEXT NOT NULL,
            violation_type TEXT NOT NULL,
            details TEXT NOT NULL,
            recovery_hint TEXT NOT NULL,
            forensic_metadata TEXT NOT NULL,
            hostname TEXT,
            process_id INTEGER,
            python_version TEXT,
            aethel_version TEXT,
            stack_trace TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for efficient querying
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_integrity_panic_timestamp 
        ON integrity_panics(timestamp)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_integrity_panic_violation_type 
        ON integrity_panics(violation_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_integrity_panic_exception_class 
        ON integrity_panics(exception_class)
    """)
    
    # Extract forensic metadata
    forensic = panic.forensic_metadata
    system_info = forensic.get("system", {})
    process_info = forensic.get("process", {})
    env_info = forensic.get("environment", {})
    
    # Insert panic record
    cursor.execute("""
        INSERT INTO integrity_panics (
            timestamp,
            timestamp_iso,
            exception_class,
            violation_type,
            details,
            recovery_hint,
            forensic_metadata,
            hostname,
            process_id,
            python_version,
            aethel_version,
            stack_trace
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        panic.timestamp,
        forensic.get("timestamp_iso"),
        panic.__class__.__name__,
        panic.violation_type,
        json.dumps(panic.details),
        panic.recovery_hint,
        json.dumps(forensic),
        system_info.get("hostname"),
        process_info.get("pid"),
        system_info.get("python_version"),
        env_info.get("aethel_version"),
        json.dumps(forensic.get("stack_trace", []))
    ))
    
    conn.commit()
    conn.close()


def query_integrity_panics(
    db_path: str = ".aethel_sentinel/telemetry.db",
    violation_type: Optional[str] = None,
    exception_class: Optional[str] = None,
    since_timestamp: Optional[float] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Query integrity panics from the audit trail.
    
    This function allows administrators to investigate integrity violations
    and analyze patterns for security monitoring.
    
    Args:
        db_path: Path to the telemetry/audit database
        violation_type: Filter by violation type (e.g., "STATE_FILE_CORRUPTED")
        exception_class: Filter by exception class (e.g., "StateCorruptionPanic")
        since_timestamp: Only return panics after this timestamp
        limit: Maximum number of records to return
    
    Returns:
        List of panic records as dictionaries
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    cursor = conn.cursor()
    
    # Build query with filters
    query = "SELECT * FROM integrity_panics WHERE 1=1"
    params = []
    
    if violation_type:
        query += " AND violation_type = ?"
        params.append(violation_type)
    
    if exception_class:
        query += " AND exception_class = ?"
        params.append(exception_class)
    
    if since_timestamp:
        query += " AND timestamp >= ?"
        params.append(since_timestamp)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Convert to list of dicts
    results = []
    for row in rows:
        record = dict(row)
        # Parse JSON fields
        record['details'] = json.loads(record['details'])
        record['forensic_metadata'] = json.loads(record['forensic_metadata'])
        record['stack_trace'] = json.loads(record['stack_trace'])
        results.append(record)
    
    conn.close()
    return results


def get_integrity_panic_stats(
    db_path: str = ".aethel_sentinel/telemetry.db"
) -> Dict[str, Any]:
    """
    Get statistics about integrity panics for monitoring dashboards.
    
    Returns:
        Dictionary with panic statistics:
        - total_panics: Total number of panics recorded
        - panics_by_type: Count by violation type
        - panics_by_class: Count by exception class
        - recent_panics_24h: Count in last 24 hours
        - most_recent: Timestamp of most recent panic
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='integrity_panics'
    """)
    if not cursor.fetchone():
        conn.close()
        return {
            "total_panics": 0,
            "panics_by_type": {},
            "panics_by_class": {},
            "recent_panics_24h": 0,
            "most_recent": None
        }
    
    # Total panics
    cursor.execute("SELECT COUNT(*) FROM integrity_panics")
    total_panics = cursor.fetchone()[0]
    
    # Panics by violation type
    cursor.execute("""
        SELECT violation_type, COUNT(*) as count 
        FROM integrity_panics 
        GROUP BY violation_type
    """)
    panics_by_type = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Panics by exception class
    cursor.execute("""
        SELECT exception_class, COUNT(*) as count 
        FROM integrity_panics 
        GROUP BY exception_class
    """)
    panics_by_class = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Recent panics (last 24 hours)
    twenty_four_hours_ago = time.time() - (24 * 60 * 60)
    cursor.execute("""
        SELECT COUNT(*) FROM integrity_panics 
        WHERE timestamp >= ?
    """, (twenty_four_hours_ago,))
    recent_panics_24h = cursor.fetchone()[0]
    
    # Most recent panic
    cursor.execute("SELECT MAX(timestamp) FROM integrity_panics")
    most_recent = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_panics": total_panics,
        "panics_by_type": panics_by_type,
        "panics_by_class": panics_by_class,
        "recent_panics_24h": recent_panics_24h,
        "most_recent": most_recent
    }


# Export all exception classes and utility functions
__all__ = [
    'IntegrityPanic',
    'StateCorruptionPanic',
    'MerkleRootMismatchPanic',
    'UnsupportedConstraintError',
    'InvalidSignaturePanic',
    'WALCorruptionPanic',
    'NodeIdentityMismatchPanic',
    'log_integrity_panic',
    'query_integrity_panics',
    'get_integrity_panic_stats',
]
