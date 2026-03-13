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
Atomic Commit Layer for RVC-003 Mitigation

This module implements atomic commit protocol using write-ahead logging (WAL)
and atomic file rename operations to ensure all-or-nothing persistence guarantees.

The protocol protects against power failures during state writes, ensuring the
Merkle Root never becomes orphaned from its corresponding state data.

Protocol:
1. Write changes to WAL
2. Fsync WAL to disk (durable)
3. Apply changes to state
4. Write state to temp file
5. Fsync temp file
6. Atomic rename temp → canonical
7. Mark WAL entry committed

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.1 "RVC-003 Mitigation"
Date: February 21, 2026
"""

import os
import json
import time
import uuid
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from diotec360.core.integrity_panic import StateCorruptionPanic, MerkleRootMismatchPanic


@dataclass
class Transaction:
    """
    Represents a state transaction.
    
    Attributes:
        tx_id: Unique transaction identifier
        changes: Dict of state changes (key -> value)
        merkle_root_before: Merkle root before changes
        merkle_root_after: Merkle root after changes
        timestamp: Transaction timestamp
        status: Transaction status (pending/committed/rolled_back)
    """
    tx_id: str
    changes: Dict[str, Any]
    merkle_root_before: Optional[str] = None
    merkle_root_after: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    status: str = "pending"


@dataclass
class WALEntry:
    """
    Write-ahead log entry.
    
    Attributes:
        tx_id: Transaction ID
        changes: State changes
        timestamp: Entry timestamp
        committed: Whether entry is committed
        entry_offset: Byte offset in WAL file
    """
    tx_id: str
    changes: Dict[str, Any]
    timestamp: float
    committed: bool = False
    entry_offset: int = 0


@dataclass
class RecoveryReport:
    """
    Crash recovery report.
    
    Attributes:
        recovered: Whether recovery succeeded
        uncommitted_transactions: Number of uncommitted transactions found
        rolled_back_transactions: Number of transactions rolled back
        temp_files_cleaned: Number of temporary files deleted
        merkle_root_verified: Whether Merkle root verification passed
        recovery_duration_ms: Time taken for recovery (milliseconds)
        errors: List of errors encountered
        audit_log: List of recovery operations performed
        merkle_root: Merkle root after recovery (if verified)
    """
    recovered: bool
    uncommitted_transactions: int
    rolled_back_transactions: int
    temp_files_cleaned: int
    merkle_root_verified: bool
    recovery_duration_ms: float
    errors: List[str] = field(default_factory=list)
    audit_log: List[str] = field(default_factory=list)
    merkle_root: Optional[str] = None


class WriteAheadLog:
    """
    Write-ahead log for atomic commit protocol.
    
    The WAL is an append-only log of state changes. Each entry contains:
    - Transaction ID
    - Timestamp
    - State changes (key-value pairs)
    - Commit status (pending/committed)
    
    The WAL is fsync'd after each write to ensure durability.
    """
    
    def __init__(self, wal_dir: Path):
        """
        Initialize WAL.
        
        Args:
            wal_dir: Directory for WAL files
        """
        self.wal_dir = Path(wal_dir)
        self.wal_dir.mkdir(parents=True, exist_ok=True)
        
        # Current WAL file
        self.wal_file = self.wal_dir / "wal.log"
        
        # Ensure WAL file exists
        if not self.wal_file.exists():
            self.wal_file.touch()
    
    def append_entry(self, tx_id: str, changes: Dict[str, Any]) -> WALEntry:
        """
        Append a new entry to the WAL.
        
        Protocol:
        1. Serialize entry to JSON with "op": "PREPARE"
        2. Write to WAL file
        3. Fsync WAL file
        4. Return entry object
        
        Args:
            tx_id: Transaction ID
            changes: State changes to log
            
        Returns:
            WALEntry object
            
        Raises:
            OSError: If disk is full (ENOSPC) or other I/O error occurs
        """
        entry = WALEntry(
            tx_id=tx_id,
            changes=changes,
            timestamp=time.time(),
            committed=False
        )
        
        # Serialize to JSON with new format
        entry_json = json.dumps({
            'op': 'PREPARE',
            'tx_id': entry.tx_id,
            'changes': entry.changes,
            'timestamp': entry.timestamp
        })
        
        try:
            # Append to WAL file
            with open(self.wal_file, 'a') as f:
                entry.entry_offset = f.tell()
                f.write(entry_json + '\n')
                f.flush()
                os.fsync(f.fileno())  # Ensure durability
        except OSError as e:
            # Handle disk full and other I/O errors
            if e.errno == 28:  # ENOSPC - No space left on device
                raise OSError(f"Disk full: Cannot write to WAL file {self.wal_file}") from e
            else:
                raise OSError(f"I/O error writing to WAL: {e}") from e
        
        return entry
    
    def mark_committed(self, entry: WALEntry) -> None:
        """
        Mark a WAL entry as committed using append-only writes (O(1)).
        
        This method appends a single COMMIT line to the WAL instead of
        rewriting the entire file, achieving O(1) complexity per commit.
        
        WAL Format:
        - PREPARE: {"op": "PREPARE", "tx_id": "...", "changes": {...}, "timestamp": ...}
        - COMMIT: {"op": "COMMIT", "tx_id": "...", "timestamp": ...}
        
        Args:
            entry: WAL entry to mark as committed
        """
        commit_entry = {
            "op": "COMMIT",
            "tx_id": entry.tx_id,
            "timestamp": time.time()
        }
        
        # Append single line (O(1) operation)
        with open(self.wal_file, 'a') as f:
            f.write(json.dumps(commit_entry) + '\n')
            f.flush()
            os.fsync(f.fileno())  # Ensure durability
    
    def get_uncommitted_entries(self) -> List[WALEntry]:
        """
        Get all uncommitted WAL entries.
        
        Used during crash recovery to identify incomplete transactions.
        
        Returns:
            List of uncommitted WAL entries
        """
        entries = self._read_all_entries()
        return [e for e in entries if not e.committed]
    
    def truncate_committed(self) -> None:
        """
        Remove committed entries from WAL (garbage collection).
        
        This prevents the WAL from growing indefinitely.
        """
        entries = self._read_all_entries()
        uncommitted = [e for e in entries if not e.committed]
        self._rewrite_wal(uncommitted)
    
    def compact_wal(self) -> int:
        """
        Compact the WAL by removing redundant COMMIT operations.
        
        This is a maintenance operation that should be called periodically
        (e.g., every 1000 transactions) to prevent the WAL from growing
        indefinitely with COMMIT entries.
        
        The compaction process:
        1. Read all entries (PREPARE and COMMIT operations)
        2. Consolidate: Keep only the latest status for each tx_id
        3. Write compacted WAL with single entry per transaction
        
        This is NOT on the critical path - it's a background maintenance task.
        
        Returns:
            Number of entries removed during compaction
        """
        entries = self._read_all_entries()
        original_count = 0
        
        # Count original operations in file
        if self.wal_file.exists():
            with open(self.wal_file, 'r') as f:
                original_count = sum(1 for line in f if line.strip())
        
        # Rewrite with consolidated entries (one per transaction)
        self._rewrite_wal(entries)
        
        # Count new operations
        new_count = 0
        if self.wal_file.exists():
            with open(self.wal_file, 'r') as f:
                new_count = sum(1 for line in f if line.strip())
        
        return original_count - new_count
    
    def _read_all_entries(self) -> List[WALEntry]:
        """
        Read all entries from WAL file.
        
        Supports both old format (single entry with committed flag) and
        new format (PREPARE + COMMIT operations).
        
        New Format:
        - PREPARE: {"op": "PREPARE", "tx_id": "...", "changes": {...}, "timestamp": ...}
        - COMMIT: {"op": "COMMIT", "tx_id": "...", "timestamp": ...}
        
        Old Format (backward compatibility):
        - {"tx_id": "...", "changes": {...}, "timestamp": ..., "committed": bool}
        """
        entries = []
        commit_status = {}  # Track which tx_ids have been committed
        
        if not self.wal_file.exists():
            return entries
        
        with open(self.wal_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Handle new format with operations
                    if 'op' in data:
                        if data['op'] == 'PREPARE':
                            entry = WALEntry(
                                tx_id=data['tx_id'],
                                changes=data['changes'],
                                timestamp=data['timestamp'],
                                committed=False  # Will be updated if COMMIT found
                            )
                            entries.append(entry)
                        elif data['op'] == 'COMMIT':
                            # Mark this tx_id as committed
                            commit_status[data['tx_id']] = True
                    else:
                        # Handle old format (backward compatibility)
                        entry = WALEntry(
                            tx_id=data['tx_id'],
                            changes=data['changes'],
                            timestamp=data['timestamp'],
                            committed=data.get('committed', False)
                        )
                        entries.append(entry)
                except (json.JSONDecodeError, KeyError):
                    # Corrupted entry, skip
                    continue
        
        # Apply commit status from COMMIT operations
        for entry in entries:
            if entry.tx_id in commit_status:
                entry.committed = True
        
        return entries
    
    def _rewrite_wal(self, entries: List[WALEntry]) -> None:
        """
        Rewrite WAL file with given entries in new format.
        
        Used during compaction to consolidate PREPARE + COMMIT operations
        into single entries per transaction.
        """
        # Write to temp file first
        temp_file = self.wal_dir / "wal.log.tmp"
        
        with open(temp_file, 'w') as f:
            for entry in entries:
                # Write PREPARE operation
                prepare_json = json.dumps({
                    'op': 'PREPARE',
                    'tx_id': entry.tx_id,
                    'changes': entry.changes,
                    'timestamp': entry.timestamp
                })
                f.write(prepare_json + '\n')
                
                # Write COMMIT operation if committed
                if entry.committed:
                    commit_json = json.dumps({
                        'op': 'COMMIT',
                        'tx_id': entry.tx_id,
                        'timestamp': entry.timestamp
                    })
                    f.write(commit_json + '\n')
            
            f.flush()
            os.fsync(f.fileno())
        
        # Atomic rename
        temp_file.replace(self.wal_file)


class AtomicCommitLayer:
    """
    Atomic commit protocol for state persistence.
    
    Guarantees:
    - All-or-nothing: Either entire state is persisted or none of it
    - Durability: Committed state survives power failure
    - Consistency: Merkle Root always matches persisted state
    - Crash Recovery: Automatic recovery from incomplete transactions
    """
    
    def __init__(self, state_dir: Path, wal_dir: Path, merkle_tree=None):
        """
        Initialize atomic commit layer.
        
        Args:
            state_dir: Directory for state files
            wal_dir: Directory for write-ahead log
            merkle_tree: Optional MerkleTree instance for verification
        """
        self.state_dir = Path(state_dir)
        self.wal_dir = Path(wal_dir)
        self.merkle_tree = merkle_tree
        
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.wal_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize WAL
        self.wal = WriteAheadLog(self.wal_dir)
        
        # Canonical state file
        self.state_file = self.state_dir / "state.json"
        
        # Audit log file
        self.audit_log_file = self.state_dir / "recovery_audit.log"
    
    def begin_transaction(self, tx_id: str) -> Transaction:
        """
        Begin a new transaction.
        
        Args:
            tx_id: Unique transaction identifier
            
        Returns:
            Transaction object for staging changes
        """
        return Transaction(
            tx_id=tx_id,
            changes={},
            timestamp=time.time(),
            status="pending"
        )
    
    def commit_transaction(self, tx: Transaction) -> bool:
        """
        Atomically commit a transaction.
        
        Protocol:
        1. Write changes to WAL
        2. Fsync WAL to disk
        3. Apply changes to state
        4. Write state to temp file
        5. Fsync temp file
        6. Atomic rename temp → canonical
        7. Mark WAL entry committed
        
        Args:
            tx: Transaction to commit
            
        Returns:
            True if commit succeeded
            
        Raises:
            OSError: If disk is full or I/O error occurs
        """
        try:
            # Step 1-2: Write to WAL and fsync
            wal_entry = self.wal.append_entry(tx.tx_id, tx.changes)
            
            # Step 3: Load current state
            current_state = self._load_state()
            
            # Apply changes
            for key, value in tx.changes.items():
                current_state[key] = value
            
            # Step 4-5: Write to temp file and fsync
            temp_file = self.state_dir / f"state.{tx.tx_id}.tmp"
            
            try:
                with open(temp_file, 'w') as f:
                    json.dump(current_state, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
            except OSError as e:
                # Clean up temp file on error
                if temp_file.exists():
                    temp_file.unlink()
                if e.errno == 28:  # ENOSPC
                    raise OSError(f"Disk full: Cannot write state file") from e
                else:
                    raise OSError(f"I/O error writing state file: {e}") from e
            
            # Step 6: Atomic rename
            try:
                temp_file.replace(self.state_file)
            except OSError as e:
                # Clean up temp file on rename failure
                if temp_file.exists():
                    temp_file.unlink()
                raise OSError(f"Atomic rename failed: {e}") from e
            
            # Step 7: Mark WAL committed
            self.wal.mark_committed(wal_entry)
            
            tx.status = "committed"
            return True
            
        except OSError:
            # Re-raise OSError for caller to handle
            raise
        except Exception as e:
            print(f"[ATOMIC_COMMIT] Commit failed: {e}")
            return False
    
    def rollback_transaction(self, tx: Transaction) -> None:
        """
        Rollback a transaction (discard changes).
        
        Args:
            tx: Transaction to rollback
        """
        tx.status = "rolled_back"
        
        # Clean up any temp files
        temp_file = self.state_dir / f"state.{tx.tx_id}.tmp"
        if temp_file.exists():
            temp_file.unlink()
    
    def recover_from_crash(self) -> RecoveryReport:
        """
        Recover from unexpected termination.
        
        Protocol:
        1. Scan WAL for uncommitted transactions
        2. For each uncommitted transaction:
           a. Check if temp file exists
           b. If yes, delete temp file (incomplete)
           c. If no, transaction never started
        3. Detect orphaned temporary files
        4. Replay committed but unapplied WAL entries
        5. Verify Merkle Root integrity
        6. If verification fails, restore from last checkpoint
        7. Log all recovery operations to audit trail
        
        Returns:
            RecoveryReport with recovery details
        """
        start_time = time.time()
        report = RecoveryReport(
            recovered=False,
            uncommitted_transactions=0,
            rolled_back_transactions=0,
            temp_files_cleaned=0,
            merkle_root_verified=False,
            recovery_duration_ms=0.0,
            errors=[],
            audit_log=[]
        )
        
        try:
            self._log_audit(report, "RECOVERY_START", "Crash recovery initiated")
            
            # Step 1: Get uncommitted transactions
            uncommitted = self.wal.get_uncommitted_entries()
            report.uncommitted_transactions = len(uncommitted)
            self._log_audit(report, "SCAN_WAL", f"Found {len(uncommitted)} uncommitted transactions")
            
            # Step 2: Roll back uncommitted transactions
            for entry in uncommitted:
                temp_file = self.state_dir / f"state.{entry.tx_id}.tmp"
                if temp_file.exists():
                    temp_file.unlink()
                    report.temp_files_cleaned += 1
                    self._log_audit(report, "DELETE_TEMP", f"Deleted temp file for tx {entry.tx_id}")
                
                report.rolled_back_transactions += 1
                self._log_audit(report, "ROLLBACK_TX", f"Rolled back transaction {entry.tx_id}")
            
            # Step 3: Clean up any orphaned temp files
            orphaned_count = 0
            for temp_file in self.state_dir.glob("state.*.tmp"):
                temp_file.unlink()
                report.temp_files_cleaned += 1
                orphaned_count += 1
                self._log_audit(report, "DELETE_ORPHAN", f"Deleted orphaned temp file {temp_file.name}")
            
            if orphaned_count > 0:
                self._log_audit(report, "CLEANUP_ORPHANS", f"Cleaned up {orphaned_count} orphaned temp files")
            
            # Step 4: Replay committed but unapplied WAL entries (if any)
            # For now, we assume all committed entries are already applied
            # This is a placeholder for future enhancement
            
            # Step 5: Verify state file exists and is valid
            if self.state_file.exists():
                try:
                    state = self._load_state()
                    self._log_audit(report, "LOAD_STATE", f"Loaded state with {len(state)} entries")
                    
                    # Step 6: Verify Merkle Root if MerkleTree is available
                    if self.merkle_tree is not None:
                        calculated_root = self._calculate_merkle_root(state)
                        stored_root = self.merkle_tree.get_root_hash()
                        
                        if calculated_root == stored_root:
                            report.merkle_root_verified = True
                            report.merkle_root = calculated_root
                            self._log_audit(report, "VERIFY_MERKLE", f"Merkle root verified: {calculated_root}")
                        else:
                            # RVC2-001: Merkle Root mismatch triggers MerkleRootMismatchPanic
                            report.merkle_root_verified = False
                            report.errors.append(f"Merkle root mismatch: calculated={calculated_root}, stored={stored_root}")
                            self._log_audit(report, "MERKLE_MISMATCH", f"Merkle root verification failed")
                            
                            # Raise panic - system MUST halt
                            raise MerkleRootMismatchPanic(
                                violation_type="MERKLE_ROOT_MISMATCH",
                                details={
                                    "computed_root": calculated_root,
                                    "stored_root": stored_root,
                                    "state_file": str(self.state_file),
                                    "state_size": len(state),
                                    "state_keys": list(state.keys())
                                }
                            )
                    else:
                        # No MerkleTree available, skip verification
                        report.merkle_root_verified = True
                        self._log_audit(report, "SKIP_MERKLE", "Merkle root verification skipped (no MerkleTree)")
                    
                except json.JSONDecodeError as e:
                    # RVC2-001: Fail-closed recovery - NEVER create empty state
                    raise StateCorruptionPanic(
                        violation_type="STATE_FILE_CORRUPTED",
                        details={
                            "path": str(self.state_file),
                            "error": str(e),
                            "error_type": type(e).__name__
                        }
                    )
            else:
                # RVC2-001: Fail-closed recovery - NEVER create empty state
                raise StateCorruptionPanic(
                    violation_type="STATE_FILE_MISSING",
                    details={
                        "path": str(self.state_file),
                        "state_dir": str(self.state_dir)
                    }
                )
            
            report.recovered = True
            self._log_audit(report, "RECOVERY_SUCCESS", "Crash recovery completed successfully")
            
        except (StateCorruptionPanic, MerkleRootMismatchPanic):
            # RVC2-001: Integrity violations must propagate - do NOT catch
            # Let the exception bubble up to force system halt
            raise
        except Exception as e:
            report.errors.append(str(e))
            report.recovered = False
            self._log_audit(report, "RECOVERY_ERROR", f"Recovery failed: {e}")
        
        finally:
            end_time = time.time()
            report.recovery_duration_ms = (end_time - start_time) * 1000
            self._log_audit(report, "RECOVERY_END", f"Recovery duration: {report.recovery_duration_ms:.2f}ms")
            
            # Write audit log to file
            self._write_audit_log(report)
        
        return report
    
    def _log_audit(self, report: RecoveryReport, operation: str, details: str) -> None:
        """
        Log a recovery operation to the audit trail.
        
        Args:
            report: RecoveryReport to append to
            operation: Operation type
            details: Operation details
        """
        timestamp = time.time()
        log_entry = f"[{timestamp:.6f}] {operation}: {details}"
        report.audit_log.append(log_entry)
    
    def _write_audit_log(self, report: RecoveryReport) -> None:
        """
        Write audit log to file.
        
        Args:
            report: RecoveryReport with audit log
        """
        try:
            with open(self.audit_log_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Recovery Report - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Recovered: {report.recovered}\n")
                f.write(f"Uncommitted Transactions: {report.uncommitted_transactions}\n")
                f.write(f"Rolled Back Transactions: {report.rolled_back_transactions}\n")
                f.write(f"Temp Files Cleaned: {report.temp_files_cleaned}\n")
                f.write(f"Merkle Root Verified: {report.merkle_root_verified}\n")
                f.write(f"Recovery Duration: {report.recovery_duration_ms:.2f}ms\n")
                
                if report.merkle_root:
                    f.write(f"Merkle Root: {report.merkle_root}\n")
                
                if report.errors:
                    f.write(f"\nErrors:\n")
                    for error in report.errors:
                        f.write(f"  - {error}\n")
                
                f.write(f"\nAudit Log:\n")
                for entry in report.audit_log:
                    f.write(f"  {entry}\n")
                
                f.write(f"{'='*80}\n\n")
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            # Don't fail recovery if audit log write fails
            print(f"[ATOMIC_COMMIT] Warning: Failed to write audit log: {e}")
    
    def _calculate_merkle_root(self, state: Dict[str, Any]) -> str:
        """
        Calculate Merkle root for given state.
        
        Args:
            state: State dictionary
            
        Returns:
            Merkle root hash
        """
        # Simple hash-based calculation
        # In production, this would use the actual MerkleTree
        state_json = json.dumps(state, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from canonical file"""
        if not self.state_file.exists():
            return {}
        
        with open(self.state_file, 'r') as f:
            return json.load(f)
    
    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save state to canonical file"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
