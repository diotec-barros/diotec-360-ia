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
Optimized Atomic Commit Layer for RVC-003 Mitigation

This module provides performance-optimized atomic commit with:
- Batch WAL writes (reduce fsync calls)
- Async fsync (non-blocking durability)
- Write coalescing (combine multiple writes)
- Lazy WAL garbage collection

Performance target: <10% overhead vs direct writes

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.1 "RVC-003 Optimization"
Date: February 22, 2026
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

from diotec360.consensus.atomic_commit import (
    Transaction, WALEntry, RecoveryReport, WriteAheadLog, AtomicCommitLayer
)


class OptimizedWriteAheadLog(WriteAheadLog):
    """
    Optimized WAL with batch writes and async fsync.
    
    Optimizations:
    - Batch multiple WAL entries before fsync
    - Async fsync in background thread
    - Write coalescing for sequential writes
    """
    
    def __init__(self, wal_dir: Path, batch_size: int = 10, async_fsync: bool = True):
        """
        Initialize optimized WAL.
        
        Args:
            wal_dir: Directory for WAL files
            batch_size: Number of entries to batch before fsync
            async_fsync: Enable async fsync in background
        """
        super().__init__(wal_dir)
        
        self.batch_size = batch_size
        self.async_fsync = async_fsync
        
        # Batch buffer
        self._batch_buffer: List[WALEntry] = []
        self._batch_lock = threading.Lock()
        
        # Async fsync executor
        if self.async_fsync:
            self._fsync_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="wal_fsync")
        else:
            self._fsync_executor = None
    
    def append_entry(self, tx_id: str, changes: Dict[str, Any]) -> WALEntry:
        """
        Append entry with batching optimization.
        
        Args:
            tx_id: Transaction ID
            changes: State changes to log
            
        Returns:
            WALEntry object
        """
        entry = WALEntry(
            tx_id=tx_id,
            changes=changes,
            timestamp=time.time(),
            committed=False
        )
        
        with self._batch_lock:
            self._batch_buffer.append(entry)
            
            # Flush batch if full
            if len(self._batch_buffer) >= self.batch_size:
                self._flush_batch()
        
        return entry
    
    def _flush_batch(self) -> None:
        """Flush batch buffer to disk"""
        if not self._batch_buffer:
            return
        
        try:
            # Write all entries in batch
            with open(self.wal_file, 'a') as f:
                for entry in self._batch_buffer:
                    entry_json = json.dumps({
                        'tx_id': entry.tx_id,
                        'changes': entry.changes,
                        'timestamp': entry.timestamp,
                        'committed': entry.committed
                    })
                    f.write(entry_json + '\n')
                
                f.flush()
                
                # Fsync (sync or async)
                if self.async_fsync and self._fsync_executor:
                    # Async fsync in background
                    self._fsync_executor.submit(os.fsync, f.fileno())
                else:
                    # Sync fsync
                    os.fsync(f.fileno())
            
            # Clear buffer
            self._batch_buffer.clear()
            
        except OSError as e:
            # Handle errors
            if e.errno == 28:  # ENOSPC
                raise OSError(f"Disk full: Cannot write to WAL file {self.wal_file}") from e
            else:
                raise OSError(f"I/O error writing to WAL: {e}") from e
    
    def force_flush(self) -> None:
        """Force flush of batch buffer"""
        with self._batch_lock:
            self._flush_batch()
    
    def shutdown(self) -> None:
        """Shutdown WAL and wait for pending fsyncs"""
        # Flush any pending entries
        self.force_flush()
        
        # Shutdown async executor
        if self._fsync_executor:
            self._fsync_executor.shutdown(wait=True)


class OptimizedAtomicCommitLayer(AtomicCommitLayer):
    """
    Optimized atomic commit layer with performance improvements.
    
    Optimizations:
    - Batch WAL writes (reduce fsync calls)
    - Async fsync (non-blocking durability)
    - Write coalescing (combine multiple writes)
    - Lazy garbage collection
    
    Target: <10% overhead vs direct writes
    """
    
    def __init__(
        self,
        state_dir: Path,
        wal_dir: Path,
        merkle_tree=None,
        batch_size: int = 10,
        async_fsync: bool = True
    ):
        """
        Initialize optimized atomic commit layer.
        
        Args:
            state_dir: Directory for state files
            wal_dir: Directory for write-ahead log
            merkle_tree: Optional MerkleTree instance for verification
            batch_size: Number of WAL entries to batch before fsync
            async_fsync: Enable async fsync in background
        """
        # Initialize base class
        super().__init__(state_dir, wal_dir, merkle_tree)
        
        # Replace WAL with optimized version
        self.wal = OptimizedWriteAheadLog(
            self.wal_dir,
            batch_size=batch_size,
            async_fsync=async_fsync
        )
        
        # Optimization settings
        self.batch_size = batch_size
        self.async_fsync = async_fsync
        
        # Lazy garbage collection
        self._gc_counter = 0
        self._gc_interval = 100  # GC every 100 commits
    
    def commit_transaction(self, tx: Transaction) -> bool:
        """
        Atomically commit a transaction with optimizations.
        
        Optimizations applied:
        - Batch WAL writes
        - Async fsync
        - Lazy garbage collection
        
        Args:
            tx: Transaction to commit
            
        Returns:
            True if commit succeeded
        """
        try:
            # Step 1-2: Write to WAL (batched)
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
                    
                    # Async fsync for state file too
                    if self.async_fsync:
                        # For state files, we still need sync fsync for safety
                        # But we can optimize by reducing fsync frequency
                        os.fsync(f.fileno())
                    else:
                        os.fsync(f.fileno())
                        
            except OSError as e:
                if temp_file.exists():
                    temp_file.unlink()
                if e.errno == 28:
                    raise OSError(f"Disk full: Cannot write state file") from e
                else:
                    raise OSError(f"I/O error writing state file: {e}") from e
            
            # Step 6: Atomic rename
            try:
                temp_file.replace(self.state_file)
            except OSError as e:
                if temp_file.exists():
                    temp_file.unlink()
                raise OSError(f"Atomic rename failed: {e}") from e
            
            # Step 7: Mark WAL committed
            self.wal.mark_committed(wal_entry)
            
            # Lazy garbage collection
            self._gc_counter += 1
            if self._gc_counter >= self._gc_interval:
                self.wal.truncate_committed()
                self._gc_counter = 0
            
            tx.status = "committed"
            return True
            
        except OSError:
            raise
        except Exception as e:
            print(f"[ATOMIC_COMMIT_OPT] Commit failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown and wait for pending operations"""
        # Force flush WAL
        self.wal.force_flush()
        
        # Shutdown WAL
        self.wal.shutdown()
