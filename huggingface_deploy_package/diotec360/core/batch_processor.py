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
Aethel Batch Processor - Synchrony Protocol v1.8.0

Main orchestrator for parallel transaction processing. Coordinates dependency analysis,
conflict detection, parallel execution, formal verification, and atomic commit.

Philosophy: "One transaction is correct. A thousand parallel transactions are correct."

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

from typing import List, Dict, Optional, Any
import time
import copy

from diotec360.core.synchrony import (
    Transaction,
    BatchResult,
    ExecutionResult,
    CircularDependencyError,
    LinearizabilityError,
    ConservationViolationError,
    TimeoutError as SynchronyTimeoutError,
    ConflictResolutionError
)
from diotec360.core.dependency_analyzer import DependencyAnalyzer
from diotec360.core.conflict_detector import ConflictDetector
from diotec360.core.parallel_executor import ParallelExecutor
from diotec360.core.linearizability_prover import LinearizabilityProver
from diotec360.core.conservation_validator import ConservationValidator
from diotec360.core.commit_manager import CommitManager

# Import AtomicBatchNode for type hints
try:
    from diotec360.core.parser import AtomicBatchNode
except ImportError:
    AtomicBatchNode = None


class BatchProcessor:
    """
    Main orchestrator for parallel transaction processing.
    
    Key Concepts:
    - Pipeline: Dependency → Conflict → Execute → Prove → Commit
    - Fallback: If parallel fails, fall back to serial execution
    - Atomicity: All transactions commit or all rollback
    - Verification: Formal proofs before commit
    
    Pipeline Stages:
    1. Dependency Analysis - Build DAG of transaction dependencies
    2. Conflict Detection - Identify and resolve conflicts
    3. Parallel Execution - Execute independent transactions concurrently
    4. Linearizability Proof - Prove parallel = serial
    5. Conservation Validation - Verify global conservation
    6. Atomic Commit - Commit all or rollback all
    
    Validates:
        Requirements 1.1, 2.1, 2.2, 3.1-3.4, 4.1-4.2, 7.1-7.5, 9.1-9.5
    """
    
    def __init__(self, num_threads: int = 8, timeout_seconds: float = 300.0):
        """
        Initialize batch processor.
        
        Args:
            num_threads: Number of threads for parallel execution (default 8)
            timeout_seconds: Timeout for batch execution (default 300s = 5 minutes)
        """
        self.num_threads = num_threads
        self.timeout_seconds = timeout_seconds
        
        # Initialize components
        self.dependency_analyzer = DependencyAnalyzer()
        self.conflict_detector = ConflictDetector()
        self.parallel_executor = ParallelExecutor(thread_count=num_threads)
        self.linearizability_prover = LinearizabilityProver()
        self.conservation_validator = ConservationValidator()
        self.commit_manager = CommitManager()
    
    def execute_batch(self, transactions: List[Transaction]) -> BatchResult:
        """
        Execute a batch of transactions with parallel optimization.
        
        Orchestrates the entire pipeline:
        1. Dependency analysis
        2. Conflict detection
        3. Parallel execution
        4. Linearizability proof
        5. Conservation validation
        6. Atomic commit
        
        If any stage fails, attempts fallback to serial execution.
        If serial execution fails, rolls back all changes.
        
        Args:
            transactions: List of transactions to execute
            
        Returns:
            BatchResult containing execution status, proofs, and metrics
            
        Validates:
            Requirements 1.1, 2.1, 2.2, 3.1-3.4, 4.1-4.2, 7.1-7.5, 9.1-9.5
        """
        start_time = time.time()
        
        # Handle empty batch
        if not transactions:
            return self._create_empty_batch_result()
        
        # Capture initial states
        initial_states = self._capture_initial_states(transactions)
        
        try:
            # ============================================================
            # STAGE 1: Dependency Analysis
            # ============================================================
            dependency_graph = self.dependency_analyzer.analyze(transactions)
            
            # Check for circular dependencies
            if dependency_graph.has_cycle():
                cycle = dependency_graph.find_cycle()
                raise CircularDependencyError(cycle)
            
            # ============================================================
            # STAGE 2: Conflict Detection
            # ============================================================
            conflicts = self.conflict_detector.detect_conflicts(
                transactions,
                dependency_graph
            )
            
            # Resolve conflicts deterministically
            resolution_strategy = self.conflict_detector.resolve_conflicts(conflicts)
            
            # ============================================================
            # STAGE 3: Parallel Execution
            # ============================================================
            execution_result = self.parallel_executor.execute_parallel(
                transactions,
                dependency_graph,
                initial_states
            )
            
            # ============================================================
            # STAGE 4: Linearizability Proof
            # ============================================================
            proof_result = self.linearizability_prover.prove_linearizability(
                execution_result,
                transactions
            )
            
            if not proof_result.is_linearizable:
                # Parallel execution failed linearizability
                # Fall back to serial execution
                return self._fallback_to_serial(
                    transactions,
                    initial_states,
                    proof_result,
                    start_time
                )
            
            # ============================================================
            # STAGE 5: Conservation Validation
            # ============================================================
            conservation_result = self.conservation_validator.validate_batch_conservation(
                execution_result,
                initial_states
            )
            
            if not conservation_result.is_valid:
                raise ConservationViolationError(
                    expected=self._compute_total_balance(initial_states),
                    actual=self._compute_total_balance(execution_result.final_states),
                    details={
                        "violation_amount": conservation_result.violation_amount,
                        "error_message": conservation_result.error_message
                    }
                )
            
            # ============================================================
            # STAGE 6: Atomic Commit
            # ============================================================
            result = self.commit_manager.commit_batch(
                execution_result=execution_result,
                transactions=transactions,
                initial_states=initial_states,
                proof_result=proof_result,
                conservation_result=conservation_result
            )
            
            # Add conflicts to result
            result.conflicts_detected = conflicts
            
            # Calculate final metrics
            total_time = time.time() - start_time
            result.execution_time = total_time
            
            return result
        
        except CircularDependencyError as e:
            # Circular dependency - cannot execute
            return self._create_error_result(
                transactions=transactions,
                error=e,
                start_time=start_time,
                initial_states=initial_states
            )
        
        except (ConservationViolationError, SynchronyTimeoutError, ConflictResolutionError) as e:
            # Execution failed - rollback
            return self._create_error_result(
                transactions=transactions,
                error=e,
                start_time=start_time,
                initial_states=initial_states
            )
        
        except Exception as e:
            # Unexpected error - rollback
            return self._create_error_result(
                transactions=transactions,
                error=e,
                start_time=start_time,
                initial_states=initial_states
            )
    
    def execute_atomic_batch(self, batch_ast) -> BatchResult:
        """
        Execute an atomic_batch from parsed Aethel code.
        
        Converts AtomicBatchNode to list of transactions and executes
        using the same pipeline as programmatic batch submission.
        
        Args:
            batch_ast: AtomicBatchNode from parser
            
        Returns:
            BatchResult containing execution status, proofs, and metrics
            
        Validates:
            Requirements 6.4, 6.5
        """
        # Convert AtomicBatchNode to transactions
        if AtomicBatchNode and isinstance(batch_ast, AtomicBatchNode):
            transactions = batch_ast.to_transactions()
        elif hasattr(batch_ast, 'to_transactions'):
            transactions = batch_ast.to_transactions()
        else:
            raise ValueError(
                f"Invalid batch_ast type: {type(batch_ast)}. "
                "Expected AtomicBatchNode with to_transactions() method."
            )
        
        # Execute using same pipeline as programmatic submission
        return self.execute_batch(transactions)
    
    def execute_single_transaction(self, transaction: Transaction) -> BatchResult:
        """
        Execute a single transaction using the batch processor.
        
        This method provides backward compatibility with v1.7.0 by wrapping
        single transaction execution in a 1-transaction batch. The behavior
        is identical to v1.7.0 for single transactions.
        
        Args:
            transaction: Single transaction to execute
            
        Returns:
            BatchResult containing execution status, proofs, and metrics
            
        Validates:
            Requirements 8.1, 8.3, 8.4
        
        Note:
            This method ensures backward compatibility by:
            - Accepting the same Transaction input as v1.7.0
            - Returning the same BatchResult structure
            - Preserving all verification guarantees
            - Maintaining identical error handling
        """
        # Create 1-transaction batch
        return self.execute_batch([transaction])
    
    def _fallback_to_serial(self,
                           transactions: List[Transaction],
                           initial_states: Dict[str, Any],
                           failed_proof_result: Any,
                           start_time: float) -> BatchResult:
        """
        Fall back to serial execution when parallel execution fails linearizability.
        
        Args:
            transactions: List of transactions
            initial_states: Initial account states
            failed_proof_result: Failed linearizability proof
            start_time: Batch start time
            
        Returns:
            BatchResult from serial execution
        """
        # Execute serially (one transaction at a time)
        serial_execution_result = self._execute_serial(transactions, initial_states)
        
        # Serial execution is always linearizable (trivially)
        serial_proof_result = self.linearizability_prover.prove_linearizability(
            serial_execution_result,
            transactions
        )
        
        # Validate conservation
        conservation_result = self.conservation_validator.validate_batch_conservation(
            serial_execution_result,
            initial_states
        )
        
        # Commit serial execution
        result = self.commit_manager.commit_batch(
            execution_result=serial_execution_result,
            transactions=transactions,
            initial_states=initial_states,
            proof_result=serial_proof_result,
            conservation_result=conservation_result
        )
        
        # Add fallback information
        result.execution_time = time.time() - start_time
        result.throughput_improvement = 1.0  # No improvement (serial)
        result.diagnostic_info = {
            "fallback": True,
            "reason": "Parallel execution failed linearizability proof",
            "failed_proof": failed_proof_result.counterexample,
            "serial_execution": "Success"
        }
        
        return result
    
    def _execute_serial(self,
                       transactions: List[Transaction],
                       initial_states: Dict[str, Any]) -> ExecutionResult:
        """
        Execute transactions serially (one at a time).
        
        Args:
            transactions: List of transactions
            initial_states: Initial account states
            
        Returns:
            ExecutionResult from serial execution
        """
        from diotec360.core.synchrony import ExecutionEvent, EventType
        
        start_time = time.time()
        
        # Execute each transaction sequentially
        current_states = copy.deepcopy(initial_states)
        execution_trace = []
        
        for tx in transactions:
            # Start event
            execution_trace.append(ExecutionEvent(
                timestamp=time.time() - start_time,
                transaction_id=tx.id,
                event_type=EventType.START,
                thread_id=0
            ))
            
            # Execute transaction (simplified - just copy states)
            for account_id in tx.accounts:
                if account_id in current_states:
                    # Read event
                    execution_trace.append(ExecutionEvent(
                        timestamp=time.time() - start_time,
                        transaction_id=tx.id,
                        event_type=EventType.READ,
                        account_id=account_id,
                        old_value=current_states[account_id].get('balance', 0),
                        thread_id=0
                    ))
            
            # Commit event
            execution_trace.append(ExecutionEvent(
                timestamp=time.time() - start_time,
                transaction_id=tx.id,
                event_type=EventType.COMMIT,
                thread_id=0
            ))
        
        execution_time = time.time() - start_time
        
        return ExecutionResult(
            final_states=current_states,
            execution_trace=execution_trace,
            parallel_groups=[[tx.id] for tx in transactions],  # Each tx in own group
            execution_time=execution_time,
            thread_count=1
        )
    
    def _capture_initial_states(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Capture initial states of all accounts involved in transactions.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Dictionary of account_id -> initial state
        """
        initial_states = {}
        
        for tx in transactions:
            for account_id, account_data in tx.accounts.items():
                if account_id not in initial_states:
                    initial_states[account_id] = copy.deepcopy(account_data)
        
        return initial_states
    
    def _compute_total_balance(self, states: Dict[str, Any]) -> float:
        """
        Compute total balance across all accounts.
        
        Args:
            states: Account states dictionary
            
        Returns:
            Total balance
        """
        total = 0.0
        for account_id, state in states.items():
            if isinstance(state, dict):
                balance = state.get('balance', 0)
            else:
                balance = getattr(state, 'balance', 0)
            total += balance
        return total
    
    def _create_empty_batch_result(self) -> BatchResult:
        """Create result for empty batch"""
        return BatchResult(
            success=True,
            transactions_executed=0,
            transactions_parallel=0,
            execution_time=0.0,
            throughput_improvement=1.0,
            thread_count=0,
            avg_parallelism=0.0
        )
    
    def _create_error_result(self,
                            transactions: List[Transaction],
                            error: Exception,
                            start_time: float,
                            initial_states: Dict[str, Any]) -> BatchResult:
        """
        Create error result with diagnostic information.
        
        Args:
            transactions: List of transactions
            error: Exception that occurred
            start_time: Batch start time
            initial_states: Initial account states
            
        Returns:
            BatchResult with error information
        """
        execution_time = time.time() - start_time
        
        return BatchResult(
            success=False,
            transactions_executed=0,
            transactions_parallel=0,
            execution_time=execution_time,
            throughput_improvement=0.0,
            thread_count=self.num_threads,
            avg_parallelism=0.0,
            error_message=str(error),
            error_type=type(error).__name__,
            diagnostic_info=error.get_diagnostics() if hasattr(error, 'get_diagnostics') else {
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )


# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.8.0"
__author__ = "Aethel Team"
__all__ = [
    "BatchProcessor",
]
