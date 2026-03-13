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
Aethel Parallel Executor - Synchrony Protocol v1.8.0

Executes independent transactions concurrently using thread pools while respecting
dependency order. Implements copy-on-write for account states, timeout mechanisms,
and comprehensive execution tracing.

Philosophy: "If one transaction is correct, a thousand parallel transactions are correct."

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError as FutureTimeoutError
import threading
import time
import copy

from diotec360.core.synchrony import (
    Transaction,
    ExecutionEvent,
    ExecutionResult,
    EventType,
    TimeoutError,
    ConservationViolationError
)
from diotec360.core.dependency_graph import DependencyGraph


@dataclass
class ExecutionContext:
    """Context for executing a single transaction"""
    transaction: Transaction
    account_states: Dict[str, Any]  # Copy-on-write account states
    thread_id: int
    start_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "transaction_id": self.transaction.id,
            "thread_id": self.thread_id,
            "start_time": self.start_time
        }


class ParallelExecutor:
    """
    Executes transactions in parallel while respecting dependencies.
    
    Key Features:
    - Thread pool for concurrent execution
    - Copy-on-write for account states (isolation)
    - Timeout mechanism to prevent deadlocks
    - Execution trace with timestamps and thread IDs
    - Respects dependency order from conflict resolution
    
    Algorithm:
    1. Get independent sets from dependency graph
    2. For each independent set:
       a. Execute all transactions in parallel (thread pool)
       b. Wait for all to complete
       c. Merge results
    3. Record execution trace with timestamps
    4. Return final states and trace
    
    Validates:
        Requirements 2.1, 2.2, 2.3, 10.3, 10.4, 10.5
    """
    
    def __init__(self, thread_count: int = 8, timeout_seconds: float = 30.0):
        """
        Initialize parallel executor.
        
        Args:
            thread_count: Number of threads in pool (default 8)
            timeout_seconds: Timeout for batch execution (default 30s)
        """
        self.thread_count = thread_count
        self.timeout_seconds = timeout_seconds
        self.executor = ThreadPoolExecutor(max_workers=thread_count)
        
        # Execution state
        self.execution_trace: List[ExecutionEvent] = []
        self.trace_lock = threading.Lock()
        self.next_thread_id = 0
        self.thread_id_lock = threading.Lock()
    
    def _get_thread_id(self) -> int:
        """Get unique thread ID for this execution"""
        with self.thread_id_lock:
            thread_id = self.next_thread_id
            self.next_thread_id += 1
            return thread_id
    
    def _record_event(self, event: ExecutionEvent):
        """Thread-safe event recording"""
        with self.trace_lock:
            self.execution_trace.append(event)
    
    def _execute_transaction(self, 
                            transaction: Transaction,
                            account_states: Dict[str, Any],
                            thread_id: int) -> Dict[str, Any]:
        """
        Execute a single transaction with copy-on-write semantics.
        
        Args:
            transaction: Transaction to execute
            account_states: Current account states (will be copied)
            thread_id: Thread ID for tracing
            
        Returns:
            Updated account states after transaction
            
        Raises:
            Exception: If transaction execution fails
        """
        start_time = time.time()
        
        # Record START event
        self._record_event(ExecutionEvent(
            timestamp=start_time,
            transaction_id=transaction.id,
            event_type=EventType.START,
            thread_id=thread_id
        ))
        
        # Copy-on-write: Create isolated copy of account states
        local_states = copy.deepcopy(account_states)
        
        # Execute transaction operations
        # For now, we simulate execution by modifying account balances
        # In real implementation, this would call the Aethel runtime
        
        for account_id, account in transaction.accounts.items():
            if account_id in local_states:
                old_value = local_states[account_id].get("balance", 0)
            else:
                old_value = 0
                local_states[account_id] = {"balance": 0}
            
            # Record READ event
            self._record_event(ExecutionEvent(
                timestamp=time.time(),
                transaction_id=transaction.id,
                event_type=EventType.READ,
                account_id=account_id,
                old_value=old_value,
                thread_id=thread_id
            ))
            
            # Simulate transaction effect (for testing)
            # In real implementation, this would execute the intent
            new_value = old_value  # Placeholder
            
            # Record WRITE event
            self._record_event(ExecutionEvent(
                timestamp=time.time(),
                transaction_id=transaction.id,
                event_type=EventType.WRITE,
                account_id=account_id,
                old_value=old_value,
                new_value=new_value,
                thread_id=thread_id
            ))
            
            local_states[account_id]["balance"] = new_value
        
        # Record COMMIT event
        self._record_event(ExecutionEvent(
            timestamp=time.time(),
            transaction_id=transaction.id,
            event_type=EventType.COMMIT,
            thread_id=thread_id
        ))
        
        return local_states
    
    def execute_independent_set(self,
                               transactions: List[Transaction],
                               initial_states: Dict[str, Any]) -> Tuple[Dict[str, Any], List[ExecutionEvent]]:
        """
        Execute a set of independent transactions in parallel.
        
        All transactions in the set are guaranteed to be independent (no conflicts),
        so they can execute concurrently without coordination.
        
        Args:
            transactions: List of independent transactions
            initial_states: Initial account states
            
        Returns:
            Tuple of (final_states, execution_events)
            
        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: If any transaction fails
            
        Validates:
            Requirements 2.1, 2.3, 10.3
        """
        if not transactions:
            return initial_states, []
        
        # Submit all transactions to thread pool
        futures: Dict[str, Future] = {}
        thread_ids: Dict[str, int] = {}
        
        for transaction in transactions:
            thread_id = self._get_thread_id()
            thread_ids[transaction.id] = thread_id
            
            future = self.executor.submit(
                self._execute_transaction,
                transaction,
                initial_states,
                thread_id
            )
            futures[transaction.id] = future
        
        # Wait for all transactions to complete (with timeout)
        completed_states: Dict[str, Dict[str, Any]] = {}
        
        try:
            for tx_id, future in futures.items():
                # Wait for this transaction with timeout
                result_states = future.result(timeout=self.timeout_seconds)
                completed_states[tx_id] = result_states
        
        except FutureTimeoutError:
            # Timeout occurred - cancel pending futures
            for future in futures.values():
                future.cancel()
            
            raise TimeoutError(
                timeout_seconds=self.timeout_seconds,
                completed=len(completed_states),
                pending=len(futures) - len(completed_states)
            )
        
        # Merge results from all transactions
        # Since transactions are independent, we can merge their state changes
        final_states = copy.deepcopy(initial_states)
        
        for tx_states in completed_states.values():
            for account_id, account_state in tx_states.items():
                final_states[account_id] = account_state
        
        return final_states, self.execution_trace.copy()
    
    def execute_parallel(self,
                        transactions: List[Transaction],
                        dependency_graph: DependencyGraph,
                        initial_states: Dict[str, Any]) -> ExecutionResult:
        """
        Execute transactions in parallel respecting dependency order.
        
        Algorithm:
        1. Get independent sets from dependency graph (topological levels)
        2. For each independent set:
           a. Execute all transactions in parallel
           b. Wait for completion
           c. Merge results
        3. Return final states and execution trace
        
        Args:
            transactions: List of transactions to execute
            dependency_graph: Dependency graph with execution order
            initial_states: Initial account states
            
        Returns:
            ExecutionResult with final states and trace
            
        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: If any transaction fails
            
        Validates:
            Requirements 2.1, 2.2, 2.3, 10.3, 10.4, 10.5
        """
        start_time = time.time()
        
        # Reset execution state
        self.execution_trace = []
        self.next_thread_id = 0
        
        # Get independent sets (transactions that can execute in parallel)
        independent_sets = dependency_graph.get_independent_sets()
        
        # Execute each independent set in parallel
        current_states = copy.deepcopy(initial_states)
        parallel_groups: List[Set[str]] = []
        
        for independent_set in independent_sets:
            # Get transactions for this set
            set_transactions = [
                tx for tx in transactions
                if tx.id in independent_set
            ]
            
            if not set_transactions:
                continue
            
            # Execute this independent set in parallel
            current_states, _ = self.execute_independent_set(
                set_transactions,
                current_states
            )
            
            # Record which transactions executed in parallel
            parallel_groups.append(independent_set)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Build execution result
        result = ExecutionResult(
            final_states=current_states,
            execution_trace=self.execution_trace.copy(),
            parallel_groups=parallel_groups,
            execution_time=execution_time,
            thread_count=self.thread_count
        )
        
        return result
    
    def shutdown(self):
        """Shutdown the thread pool"""
        self.executor.shutdown(wait=True)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()
        return False


# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.8.0"
__author__ = "Aethel Team"
__all__ = [
    "ParallelExecutor",
    "ExecutionContext",
]
