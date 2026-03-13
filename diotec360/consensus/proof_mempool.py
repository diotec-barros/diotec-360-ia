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
Proof Mempool for Proof-of-Proof consensus protocol.

This module implements a priority queue for pending proofs awaiting verification.
Proofs are ordered by difficulty (highest first) to maximize network rewards.
"""

import heapq
import time
import hashlib
import json
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from threading import Lock

from diotec360.consensus.data_models import ProofBlock
from diotec360.consensus.proof_verifier import ProofVerifier


# Forward declaration to avoid circular import
class MetricsCollector:
    """Forward declaration for type hints."""
    pass


@dataclass(order=True)
class PendingProof:
    """
    A proof pending verification in the mempool.
    
    Uses priority queue ordering where higher difficulty = higher priority.
    The dataclass order=True with difficulty as first field ensures correct heap ordering.
    """
    # Priority field (negative for max-heap behavior)
    priority: int = field(compare=True)
    
    # Proof data (not used in comparison)
    proof: Any = field(compare=False)
    proof_hash: str = field(compare=False, default="")
    difficulty: int = field(compare=False, default=0)
    timestamp: int = field(compare=False, default_factory=lambda: int(time.time()))
    
    def __post_init__(self):
        """Calculate proof hash and set priority."""
        if not self.proof_hash:
            self.proof_hash = hashlib.sha256(
                json.dumps(self.proof).encode()
            ).hexdigest()
        
        # Priority is negative difficulty for max-heap behavior
        # (Python heapq is a min-heap, so we negate to get max-heap)
        self.priority = -self.difficulty


class ProofMempool:
    """
    Priority queue for pending proofs awaiting consensus.
    
    The mempool maintains proofs ordered by difficulty (highest first) to maximize
    network rewards. It provides thread-safe operations for adding, retrieving,
    and removing proofs.
    
    Key features:
    - Priority queue ordered by difficulty (highest first)
    - Deduplication by proof hash
    - Thread-safe operations
    - Configurable maximum size
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        proof_verifier: Optional[ProofVerifier] = None,
        metrics_collector: Optional['MetricsCollector'] = None,
    ):
        """
        Initialize ProofMempool.
        
        Args:
            max_size: Maximum number of proofs to store
            proof_verifier: ProofVerifier instance for difficulty calculation
            metrics_collector: MetricsCollector instance for metrics emission
        """
        self.max_size = max_size
        self.proof_verifier = proof_verifier or ProofVerifier()
        self.metrics_collector = metrics_collector
        
        # Priority queue (min-heap with negative priorities for max-heap behavior)
        self._heap: List[PendingProof] = []
        
        # Set of proof hashes for deduplication
        self._proof_hashes: Set[str] = set()
        
        # Lock for thread-safe operations
        self._lock = Lock()
        
        # Statistics
        self._total_added = 0
        self._total_removed = 0
        self._total_rejected = 0
    
    def add_proof(self, proof: Any, difficulty: Optional[int] = None) -> bool:
        """
        Add a proof to the mempool.
        
        If difficulty is not provided, it will be calculated using the proof verifier.
        Proofs are deduplicated by hash - duplicate proofs are rejected.
        
        Args:
            proof: Proof object to add
            difficulty: Pre-calculated difficulty (optional)
            
        Returns:
            True if proof was added, False if rejected (duplicate or mempool full)
        """
        with self._lock:
            # Calculate proof hash
            proof_hash = hashlib.sha256(
                json.dumps(proof).encode()
            ).hexdigest()
            
            # Check for duplicates
            if proof_hash in self._proof_hashes:
                self._total_rejected += 1
                return False
            
            # Check mempool size
            if len(self._heap) >= self.max_size:
                # Reject if mempool is full
                self._total_rejected += 1
                return False
            
            # Calculate difficulty if not provided
            if difficulty is None:
                verification_result = self.proof_verifier.verify_proof(proof)
                if not verification_result.valid:
                    # Reject invalid proofs
                    self._total_rejected += 1
                    return False
                difficulty = verification_result.difficulty
            
            # Create pending proof
            pending = PendingProof(
                priority=-difficulty,  # Negative for max-heap
                proof=proof,
                proof_hash=proof_hash,
                difficulty=difficulty,
                timestamp=int(time.time())
            )
            
            # Add to heap and hash set
            heapq.heappush(self._heap, pending)
            self._proof_hashes.add(proof_hash)
            
            self._total_added += 1
            
            # Update metrics (Property 33: Real-Time Mempool Metrics)
            self._update_metrics()
            
            return True
    
    def get_next_block(
        self,
        block_size: int = 10,
        proposer_id: str = "unknown"
    ) -> Optional[ProofBlock]:
        """
        Select proofs for the next consensus block.
        
        Selects up to block_size proofs with highest difficulty from the mempool.
        Proofs are NOT removed from the mempool - use remove_proof() after consensus.
        
        Args:
            block_size: Maximum number of proofs to include
            proposer_id: ID of the node proposing this block
            
        Returns:
            ProofBlock with selected proofs, or None if mempool is empty
        """
        with self._lock:
            if not self._heap:
                return None
            
            # Get top proofs without removing them
            # We need to peek at the heap without modifying it
            selected_proofs = []
            
            # Create a copy of the heap to peek at top elements
            heap_copy = self._heap.copy()
            
            for _ in range(min(block_size, len(heap_copy))):
                if heap_copy:
                    pending = heapq.heappop(heap_copy)
                    selected_proofs.append(pending.proof)
            
            if not selected_proofs:
                return None
            
            # Create proof block
            block = ProofBlock(
                block_id=self._generate_block_id(),
                timestamp=int(time.time()),
                proofs=selected_proofs,
                previous_block_hash="",  # Will be set by consensus engine
                proposer_id=proposer_id,
                signature=b""  # Will be signed by consensus engine
            )
            
            return block
    
    def remove_proof(self, proof_hash: str) -> bool:
        """
        Remove a proof from the mempool after consensus.
        
        This should be called after a proof has been successfully included in
        a finalized consensus block.
        
        Args:
            proof_hash: Hash of the proof to remove
            
        Returns:
            True if proof was removed, False if not found
        """
        with self._lock:
            if proof_hash not in self._proof_hashes:
                return False
            
            # Remove from hash set
            self._proof_hashes.remove(proof_hash)
            
            # Remove from heap (requires rebuilding heap)
            # This is O(n) but acceptable for mempool operations
            self._heap = [p for p in self._heap if p.proof_hash != proof_hash]
            heapq.heapify(self._heap)
            
            self._total_removed += 1
            
            # Update metrics (Property 33: Real-Time Mempool Metrics)
            self._update_metrics()
            
            return True
    
    def remove_proofs(self, proof_hashes: List[str]) -> int:
        """
        Remove multiple proofs from the mempool.
        
        More efficient than calling remove_proof() multiple times.
        
        Args:
            proof_hashes: List of proof hashes to remove
            
        Returns:
            Number of proofs actually removed
        """
        with self._lock:
            # Convert to set for O(1) lookup
            hashes_to_remove = set(proof_hashes)
            
            # Count how many we'll actually remove
            removed_count = len(hashes_to_remove & self._proof_hashes)
            
            # Remove from hash set
            self._proof_hashes -= hashes_to_remove
            
            # Remove from heap
            self._heap = [
                p for p in self._heap
                if p.proof_hash not in hashes_to_remove
            ]
            heapq.heapify(self._heap)
            
            self._total_removed += removed_count
            
            # Update metrics (Property 33: Real-Time Mempool Metrics)
            self._update_metrics()
            
            return removed_count
    
    def size(self) -> int:
        """
        Get current number of proofs in mempool.
        
        Returns:
            Number of pending proofs
        """
        with self._lock:
            return len(self._heap)
    
    def is_empty(self) -> bool:
        """
        Check if mempool is empty.
        
        Returns:
            True if no proofs in mempool
        """
        with self._lock:
            return len(self._heap) == 0
    
    def contains(self, proof_hash: str) -> bool:
        """
        Check if a proof is in the mempool.
        
        Args:
            proof_hash: Hash of the proof to check
            
        Returns:
            True if proof is in mempool
        """
        with self._lock:
            return proof_hash in self._proof_hashes
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get mempool statistics.
        
        Returns:
            Dictionary with mempool metrics
        """
        with self._lock:
            return {
                'size': len(self._heap),
                'max_size': self.max_size,
                'total_added': self._total_added,
                'total_removed': self._total_removed,
                'total_rejected': self._total_rejected,
                'utilization': len(self._heap) / self.max_size if self.max_size > 0 else 0
            }
    
    def clear(self) -> None:
        """
        Clear all proofs from the mempool.
        
        This is primarily for testing purposes.
        """
        with self._lock:
            self._heap.clear()
            self._proof_hashes.clear()
    
    def _generate_block_id(self) -> str:
        """
        Generate a unique block ID.
        
        Returns:
            Unique block identifier
        """
        timestamp = int(time.time() * 1000000)  # microseconds
        data = f"block_{timestamp}_{len(self._heap)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _update_metrics(self) -> None:
        """
        Update mempool metrics in the metrics collector.
        
        This method implements Property 33: Real-Time Mempool Metrics.
        """
        if self.metrics_collector:
            self.metrics_collector.update_mempool_metrics(
                size=len(self._heap),
                max_size=self.max_size,
                total_added=self._total_added,
                total_removed=self._total_removed,
                total_rejected=self._total_rejected,
            )
