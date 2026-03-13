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
Aethel Synchrony Protocol v1.8.0 - "Breaking the Time Barrier"

Enables parallel transaction processing with mathematical correctness guarantees.
Analyzes dependencies, executes independent transactions concurrently, and proves
that parallel execution is equivalent to serial execution.

Philosophy: "If one transaction is correct, a thousand parallel transactions are correct."

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any, Union
from enum import Enum
import time

# Import DependencyGraph from separate module
from diotec360.core.dependency_graph import DependencyGraph, TransactionNode


# ============================================================================
# ENUMS
# ============================================================================

class ConflictType(Enum):
    """Types of conflicts between transactions"""
    RAW = "READ_AFTER_WRITE"   # T1 writes X, T2 reads X
    WAW = "WRITE_AFTER_WRITE"  # T1 writes X, T2 writes X
    WAR = "WRITE_AFTER_READ"   # T1 reads X, T2 writes X


class EventType(Enum):
    """Types of events in execution trace"""
    START = "START"
    READ = "READ"
    WRITE = "WRITE"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"


# ============================================================================
# EXCEPTIONS
# ============================================================================

class CircularDependencyError(Exception):
    """Raised when dependency graph contains a cycle"""
    
    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        super().__init__(f"Circular dependency detected: {' → '.join(cycle)}")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Return diagnostic information"""
        return {
            "error_type": "CircularDependencyError",
            "cycle": self.cycle,
            "cycle_length": len(self.cycle),
            "hint": "Modify transactions to break the circular dependency"
        }


class LinearizabilityError(Exception):
    """Raised when no valid serial order exists for parallel execution"""
    
    def __init__(self, counterexample: Dict[str, Any]):
        self.counterexample = counterexample
        super().__init__("Linearizability proof failed - no equivalent serial order exists")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Return diagnostic information"""
        return {
            "error_type": "LinearizabilityError",
            "counterexample": self.counterexample,
            "hint": "System will fall back to serial execution"
        }


class ConservationViolationError(Exception):
    """Raised when total balance changes across batch"""
    
    def __init__(self, expected: float, actual: float, details: Dict[str, Any]):
        self.expected = expected
        self.actual = actual
        self.details = details
        super().__init__(f"Conservation violated: expected {expected}, got {actual}")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Return diagnostic information"""
        return {
            "error_type": "ConservationViolationError",
            "expected_total": self.expected,
            "actual_total": self.actual,
            "violation_amount": self.actual - self.expected,
            "details": self.details,
            "hint": "Check transaction arithmetic - sum of changes must equal zero"
        }


class TimeoutError(Exception):
    """Raised when batch execution exceeds timeout"""
    
    def __init__(self, timeout_seconds: float, completed: int, pending: int):
        self.timeout_seconds = timeout_seconds
        self.completed = completed
        self.pending = pending
        super().__init__(f"Batch execution timeout after {timeout_seconds}s")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Return diagnostic information"""
        return {
            "error_type": "TimeoutError",
            "timeout_seconds": self.timeout_seconds,
            "transactions_completed": self.completed,
            "transactions_pending": self.pending,
            "hint": "Retry with smaller batch or increase timeout"
        }


class ConflictResolutionError(Exception):
    """Raised when conflicts cannot be resolved deterministically"""
    
    def __init__(self, conflicts: List['Conflict']):
        self.conflicts = conflicts
        super().__init__(f"Cannot resolve {len(conflicts)} conflicts")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Return diagnostic information"""
        return {
            "error_type": "ConflictResolutionError",
            "conflict_count": len(self.conflicts),
            "conflicts": [c.to_dict() for c in self.conflicts],
            "hint": "Modify transactions to remove conflicts"
        }


class OracleValidationError(Exception):
    """Raised when oracle proof validation fails"""
    
    def __init__(self, oracle_id: str, details: Dict[str, Any]):
        self.oracle_id = oracle_id
        self.details = details
        super().__init__(f"Oracle validation failed for '{oracle_id}'")
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Return diagnostic information"""
        return {
            "error_type": "OracleValidationError",
            "oracle_id": self.oracle_id,
            "details": self.details,
            "hint": "Provide valid oracle proof with fresh signature"
        }


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Transaction:
    """Represents a single transaction in a batch"""
    id: str
    intent_name: str
    accounts: Dict[str, Any]  # account_id -> Account object
    operations: List[Any]  # List of operations to perform
    verify_conditions: List[str]  # Verification conditions
    oracle_proofs: List[Any] = field(default_factory=list)  # Oracle proofs if needed
    
    # Cached read/write sets for performance
    _read_set: Optional[Set[str]] = field(default=None, init=False, repr=False)
    _write_set: Optional[Set[str]] = field(default=None, init=False, repr=False)
    
    def get_read_set(self) -> Set[str]:
        """Return set of account IDs read by this transaction"""
        if self._read_set is None:
            # Extract from operations and verify conditions
            self._read_set = set()
            # TODO: Implement actual extraction logic
            for account_id in self.accounts.keys():
                self._read_set.add(account_id)
        return self._read_set
    
    def get_write_set(self) -> Set[str]:
        """Return set of account IDs written by this transaction"""
        if self._write_set is None:
            # Extract from operations
            self._write_set = set()
            # TODO: Implement actual extraction logic
            for account_id in self.accounts.keys():
                self._write_set.add(account_id)
        return self._write_set
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "intent_name": self.intent_name,
            "accounts": list(self.accounts.keys()),
            "read_set": list(self.get_read_set()),
            "write_set": list(self.get_write_set())
        }


@dataclass
class Conflict:
    """Represents a conflict between two transactions"""
    type: ConflictType
    transaction_1: str  # First transaction ID
    transaction_2: str  # Second transaction ID
    resource: str  # Conflicting account/resource
    resolution: str = "enforce_order"  # "enforce_order" or "serialize"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "transaction_1": self.transaction_1,
            "transaction_2": self.transaction_2,
            "resource": self.resource,
            "resolution": self.resolution
        }


@dataclass
class ExecutionEvent:
    """Represents a single event in the execution trace"""
    timestamp: float
    transaction_id: str
    event_type: EventType
    account_id: Optional[str] = None
    old_value: Optional[int] = None
    new_value: Optional[int] = None
    thread_id: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "transaction_id": self.transaction_id,
            "event_type": self.event_type.value,
            "account_id": self.account_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "thread_id": self.thread_id
        }


@dataclass
class ExecutionResult:
    """Result of parallel execution"""
    final_states: Dict[str, Any]  # account_id -> final state
    execution_trace: List[ExecutionEvent]  # Ordered list of events
    parallel_groups: List[Set[str]]  # Groups executed in parallel
    execution_time: float  # Total execution time in seconds
    thread_count: int  # Number of threads used
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "final_states": self.final_states,
            "execution_trace": [e.to_dict() for e in self.execution_trace],
            "parallel_groups": [list(g) for g in self.parallel_groups],
            "execution_time": self.execution_time,
            "thread_count": self.thread_count
        }


@dataclass
class ProofResult:
    """Result of linearizability proof"""
    is_linearizable: bool
    serial_order: Optional[List[str]] = None  # Equivalent serial order if linearizable
    proof: Optional[str] = None  # Z3 proof if linearizable
    counterexample: Optional[Dict] = None  # Counterexample if not linearizable
    proof_time: float = 0.0  # Time to generate proof in seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_linearizable": self.is_linearizable,
            "serial_order": self.serial_order,
            "proof": self.proof,
            "counterexample": self.counterexample,
            "proof_time": self.proof_time
        }


@dataclass
class BatchResult:
    """Result of batch execution"""
    success: bool
    transactions_executed: int
    transactions_parallel: int
    execution_time: float
    throughput_improvement: float  # Ratio vs serial execution
    
    # Proof artifacts
    linearizability_proof: Optional[ProofResult] = None
    conservation_proof: Optional[Any] = None  # ConservationResult from v1.3.0
    
    # Execution details
    execution_trace: List[ExecutionEvent] = field(default_factory=list)
    parallel_groups: List[Set[str]] = field(default_factory=list)
    conflicts_detected: List[Conflict] = field(default_factory=list)
    
    # Performance metrics
    thread_count: int = 0
    avg_parallelism: float = 0.0  # Average number of concurrent transactions
    
    # Error information (if failed)
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    failed_transaction: Optional[str] = None
    counterexample: Optional[Dict] = None
    diagnostic_info: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "transactions_executed": self.transactions_executed,
            "transactions_parallel": self.transactions_parallel,
            "execution_time": self.execution_time,
            "throughput_improvement": self.throughput_improvement,
            "linearizability_proof": self.linearizability_proof.to_dict() if self.linearizability_proof else None,
            "execution_trace": [e.to_dict() for e in self.execution_trace],
            "parallel_groups": [list(g) for g in self.parallel_groups],
            "conflicts_detected": [c.to_dict() for c in self.conflicts_detected],
            "thread_count": self.thread_count,
            "avg_parallelism": self.avg_parallelism,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "failed_transaction": self.failed_transaction,
            "diagnostic_info": self.diagnostic_info
        }


# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.8.0"
__author__ = "Aethel Team"
__all__ = [
    # Enums
    "ConflictType",
    "EventType",
    # Exceptions
    "CircularDependencyError",
    "LinearizabilityError",
    "ConservationViolationError",
    "TimeoutError",
    "ConflictResolutionError",
    "OracleValidationError",
    # Data Models
    "Transaction",
    "Conflict",
    "ExecutionEvent",
    "ExecutionResult",
    "ProofResult",
    "BatchResult",
    "TransactionNode",
    "DependencyGraph",
]
