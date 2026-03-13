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
Quarantine System - Transaction Isolation

This module implements transaction isolation for suspicious transactions without
halting the entire system. It uses the existing Parallel Executor to segregate
suspicious transactions from normal ones, allowing legitimate transactions to
proceed while anomalous ones are isolated and verified separately.

Key Components:
- QuarantineEntry: Record of quarantined transaction with metadata
- BatchSegmentation: Result of batch segregation (normal vs quarantine)
- QuarantineSystem: Main class managing isolation and reintegration
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import hashlib
import json


@dataclass
class QuarantineEntry:
    """
    Record of a quarantined transaction.
    
    Attributes:
        transaction_id: Unique identifier for the transaction
        code: The transaction code that was quarantined
        reason: Why the transaction was quarantined
        anomaly_score: Score indicating how anomalous the transaction is
        timestamp: When the transaction was quarantined
        status: Current status (quarantined, cleared, rejected)
    """
    transaction_id: str
    code: str
    reason: str
    anomaly_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "quarantined"  # quarantined, cleared, rejected
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "transaction_id": self.transaction_id,
            "code": self.code,
            "reason": self.reason,
            "anomaly_score": self.anomaly_score,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }


@dataclass
class BatchSegmentation:
    """
    Result of batch segregation into normal and quarantine groups.
    
    Attributes:
        normal_transactions: List of transactions that passed anomaly checks
        quarantine_transactions: List of transactions flagged as anomalous
        total_count: Total number of transactions in the batch
        anomaly_rate: Percentage of transactions that were quarantined
    """
    normal_transactions: List[Dict[str, Any]]
    quarantine_transactions: List[QuarantineEntry]
    total_count: int
    anomaly_rate: float
    
    def __post_init__(self):
        """Validate segmentation"""
        assert len(self.normal_transactions) + len(self.quarantine_transactions) == self.total_count
        expected_rate = len(self.quarantine_transactions) / self.total_count if self.total_count > 0 else 0.0
        assert abs(self.anomaly_rate - expected_rate) < 0.01  # Allow small floating point error


class QuarantineSystem:
    """
    Manages transaction isolation and reintegration.
    
    This system:
    - Segregates suspicious transactions from normal ones
    - Processes quarantined transactions in isolation
    - Maintains a quarantine log with capacity limits
    - Performs Merkle tree operations for branch removal/reintegration
    """
    
    def __init__(self, max_capacity: int = 100):
        """
        Initialize quarantine system.
        
        Args:
            max_capacity: Maximum number of entries in quarantine log
        """
        self.max_capacity = max_capacity
        self.quarantine_log: List[QuarantineEntry] = []
        self.merkle_tree: Dict[str, Any] = {}  # Simplified Merkle tree
    
    def segment_batch(
        self,
        transactions: List[Dict[str, Any]],
        anomaly_scores: Dict[str, float],
        threshold: float = 0.7
    ) -> BatchSegmentation:
        """
        Segment batch into normal and quarantine groups.
        
        Args:
            transactions: List of transactions to segment
            anomaly_scores: Dictionary mapping transaction IDs to anomaly scores
            threshold: Anomaly score threshold for quarantine (default 0.7)
        
        Returns:
            BatchSegmentation with normal and quarantine groups
        """
        normal = []
        quarantine = []
        
        for tx in transactions:
            tx_id = tx.get("id", self._generate_tx_id(tx))
            score = anomaly_scores.get(tx_id, 0.0)
            
            if score >= threshold:
                # Quarantine this transaction
                entry = QuarantineEntry(
                    transaction_id=tx_id,
                    code=tx.get("code", ""),
                    reason=f"Anomaly score {score:.2f} exceeds threshold {threshold}",
                    anomaly_score=score
                )
                quarantine.append(entry)
            else:
                # Normal transaction
                normal.append(tx)
        
        total = len(transactions)
        anomaly_rate = len(quarantine) / total if total > 0 else 0.0
        
        return BatchSegmentation(
            normal_transactions=normal,
            quarantine_transactions=quarantine,
            total_count=total,
            anomaly_rate=anomaly_rate
        )
    
    def process_quarantined(
        self,
        quarantine_entries: List[QuarantineEntry],
        verification_func: callable
    ) -> Dict[str, List[QuarantineEntry]]:
        """
        Process quarantined transactions in isolation.
        
        Args:
            quarantine_entries: List of quarantined transactions
            verification_func: Function to verify each transaction
        
        Returns:
            Dictionary with 'cleared' and 'rejected' lists
        """
        cleared = []
        rejected = []
        
        for entry in quarantine_entries:
            try:
                # Verify in isolation
                result = verification_func(entry.code)
                
                if result.get("status") == "PROVED":
                    entry.status = "cleared"
                    cleared.append(entry)
                else:
                    entry.status = "rejected"
                    rejected.append(entry)
            except Exception as e:
                # Verification failed
                entry.status = "rejected"
                entry.reason += f" | Verification error: {str(e)}"
                rejected.append(entry)
        
        return {
            "cleared": cleared,
            "rejected": rejected
        }
    
    def add_to_log(self, entry: QuarantineEntry) -> bool:
        """
        Add entry to quarantine log.
        
        Args:
            entry: QuarantineEntry to add
        
        Returns:
            True if added successfully, False if capacity exceeded
        """
        if len(self.quarantine_log) >= self.max_capacity:
            return False
        
        self.quarantine_log.append(entry)
        return True
    
    def get_retry_after(self) -> int:
        """
        Calculate retry-after time in seconds when capacity is exceeded.
        
        Returns:
            Number of seconds to wait before retrying
        """
        # Simple strategy: wait 60 seconds
        return 60
    
    def merkle_amputate(self, transaction_id: str) -> bool:
        """
        Remove compromised branch from Merkle tree.
        
        Args:
            transaction_id: ID of transaction to remove
        
        Returns:
            True if removed successfully
        """
        if transaction_id in self.merkle_tree:
            # Remove the transaction and its descendants
            self._remove_branch(transaction_id)
            return True
        return False
    
    def reintegrate(self, entry: QuarantineEntry) -> bool:
        """
        Reintegrate cleared transaction into main tree.
        
        Args:
            entry: QuarantineEntry that was cleared
        
        Returns:
            True if reintegrated successfully
        """
        if entry.status != "cleared":
            return False
        
        # Add back to Merkle tree
        tx_hash = self._calculate_hash(entry.code)
        self.merkle_tree[entry.transaction_id] = {
            "hash": tx_hash,
            "code": entry.code,
            "timestamp": entry.timestamp.isoformat()
        }
        
        return True
    
    def get_log(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get quarantine log entries.
        
        Args:
            limit: Maximum number of entries to return (None for all)
        
        Returns:
            List of quarantine entries as dictionaries
        """
        entries = self.quarantine_log[-limit:] if limit else self.quarantine_log
        return [entry.to_dict() for entry in entries]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get quarantine statistics.
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.quarantine_log)
        cleared = sum(1 for e in self.quarantine_log if e.status == "cleared")
        rejected = sum(1 for e in self.quarantine_log if e.status == "rejected")
        quarantined = sum(1 for e in self.quarantine_log if e.status == "quarantined")
        
        return {
            "total_entries": total,
            "cleared": cleared,
            "rejected": rejected,
            "quarantined": quarantined,
            "capacity": self.max_capacity,
            "utilization": total / self.max_capacity if self.max_capacity > 0 else 0.0
        }
    
    def _generate_tx_id(self, transaction: Dict[str, Any]) -> str:
        """Generate unique transaction ID from transaction data"""
        tx_str = json.dumps(transaction, sort_keys=True)
        return hashlib.sha256(tx_str.encode()).hexdigest()[:16]
    
    def _calculate_hash(self, code: str) -> str:
        """Calculate SHA256 hash of code"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def _remove_branch(self, transaction_id: str) -> None:
        """Remove transaction and its descendants from Merkle tree"""
        if transaction_id in self.merkle_tree:
            del self.merkle_tree[transaction_id]
            
            # In a real implementation, would also remove descendants
            # For now, simplified to just remove the transaction itself
