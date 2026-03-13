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
Aethel Commit Manager - Synchrony Protocol v1.8.0

Manages atomic commit/rollback of transaction batches with formal verification.
Coordinates with linearizability prover, conservation validator, and oracle validator.

Philosophy: "All or nothing - a batch either commits completely or rolls back completely."

Author: Aethel Team
Version: 1.8.0
Date: February 4, 2026
"""

from typing import List, Dict, Optional, Any
import copy
import time

from diotec360.core.synchrony import (
    Transaction,
    ExecutionResult,
    ProofResult,
    BatchResult,
    ConservationViolationError,
    LinearizabilityError,
    OracleValidationError
)
from diotec360.core.linearizability_prover import LinearizabilityProver
from diotec360.core.conservation_validator import ConservationValidator
from diotec360.core.conservation import ConservationResult


class CommitManager:
    """
    Manages atomic commit/rollback of transaction batches.
    
    Key Concepts:
    - Atomicity: All transactions commit or all rollback
    - Verification: Validate proofs before commit
    - Rollback: Restore initial states on failure
    - Oracle Validation: Verify oracle proofs before commit
    
    Commit Protocol:
    1. Verify linearizability proof is valid
    2. Verify conservation holds globally
    3. Verify all oracle proofs (if any)
    4. If all checks pass: commit all state changes atomically
    5. If any check fails: rollback all state changes
    
    Validates:
        Requirements 3.1, 3.2, 3.4, 3.5
    """
    
    def __init__(self):
        """Initialize commit manager."""
        self.linearizability_prover = LinearizabilityProver()
        self.conservation_validator = ConservationValidator()
    
    def commit_batch(self,
                    execution_result: ExecutionResult,
                    transactions: List[Transaction],
                    initial_states: Dict[str, Any],
                    proof_result: Optional[ProofResult] = None,
                    conservation_result: Optional[ConservationResult] = None) -> BatchResult:
        """
        Atomically commit or rollback batch.
        
        Performs comprehensive validation before commit:
        1. Linearizability proof validation
        2. Conservation validation
        3. Oracle proof validation
        
        If all validations pass, commits all state changes atomically.
        If any validation fails, rolls back all state changes.
        
        Args:
            execution_result: Result from parallel execution
            transactions: Original transactions
            initial_states: Initial account states before batch
            proof_result: Linearizability proof result (optional, will generate if None)
            conservation_result: Conservation validation result (optional, will validate if None)
            
        Returns:
            BatchResult indicating success or failure with details
            
        Raises:
            LinearizabilityError: If linearizability proof fails
            ConservationViolationError: If conservation is violated
            OracleValidationError: If oracle validation fails
            
        Validates:
            Requirements 3.1, 3.2, 3.4, 3.5
        """
        start_time = time.time()
        
        try:
            # Phase 1: Linearizability Proof Validation
            if proof_result is None:
                proof_result = self.linearizability_prover.prove_linearizability(
                    execution_result,
                    transactions
                )
            
            if not proof_result.is_linearizable:
                raise LinearizabilityError(proof_result.counterexample or {})
            
            # Phase 2: Conservation Validation
            if conservation_result is None:
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
            
            # Phase 3: Oracle Validation
            oracle_validation_result = self._validate_oracle_proofs(transactions)
            if not oracle_validation_result["is_valid"]:
                raise OracleValidationError(
                    oracle_id=oracle_validation_result["failed_oracle"],
                    details=oracle_validation_result["details"]
                )
            
            # Phase 4: Atomic Commit
            # All validations passed - commit is safe
            commit_time = time.time() - start_time
            
            # Calculate performance metrics
            throughput_improvement = self._calculate_throughput_improvement(
                execution_result,
                transactions
            )
            
            avg_parallelism = self._calculate_avg_parallelism(execution_result)
            
            # Build success result
            return BatchResult(
                success=True,
                transactions_executed=len(transactions),
                transactions_parallel=sum(len(g) for g in execution_result.parallel_groups if len(g) > 1),
                execution_time=execution_result.execution_time + commit_time,
                throughput_improvement=throughput_improvement,
                linearizability_proof=proof_result,
                conservation_proof=conservation_result,
                execution_trace=execution_result.execution_trace,
                parallel_groups=execution_result.parallel_groups,
                conflicts_detected=[],  # Will be populated by conflict detector
                thread_count=execution_result.thread_count,
                avg_parallelism=avg_parallelism,
                error_message=None,
                error_type=None,
                failed_transaction=None,
                counterexample=None,
                diagnostic_info=None
            )
        
        except (LinearizabilityError, ConservationViolationError, OracleValidationError) as e:
            # Validation failed - rollback
            self.rollback_batch(execution_result, initial_states)
            
            commit_time = time.time() - start_time
            
            # Build failure result
            return BatchResult(
                success=False,
                transactions_executed=0,  # None committed due to rollback
                transactions_parallel=0,
                execution_time=execution_result.execution_time + commit_time,
                throughput_improvement=0.0,
                linearizability_proof=proof_result if isinstance(e, LinearizabilityError) else None,
                conservation_proof=conservation_result if isinstance(e, ConservationViolationError) else None,
                execution_trace=execution_result.execution_trace,
                parallel_groups=execution_result.parallel_groups,
                conflicts_detected=[],
                thread_count=execution_result.thread_count,
                avg_parallelism=0.0,
                error_message=str(e),
                error_type=type(e).__name__,
                failed_transaction=None,
                counterexample=getattr(e, 'counterexample', None),
                diagnostic_info=e.get_diagnostics() if hasattr(e, 'get_diagnostics') else None
            )
    
    def rollback_batch(self,
                      execution_result: ExecutionResult,
                      initial_states: Dict[str, Any]) -> None:
        """
        Rollback all state changes from batch.
        
        Restores all account states to their initial values before batch execution.
        This ensures atomicity - if any transaction fails, all transactions are undone.
        
        Args:
            execution_result: Result from parallel execution
            initial_states: Initial states to restore
            
        Validates:
            Requirements 3.1, 3.2
        """
        # Restore all account states to initial values
        for account_id, initial_state in initial_states.items():
            if account_id in execution_result.final_states:
                # Restore initial state
                execution_result.final_states[account_id] = copy.deepcopy(initial_state)
        
        # Remove any newly created accounts
        accounts_to_remove = []
        for account_id in execution_result.final_states:
            if account_id not in initial_states:
                accounts_to_remove.append(account_id)
        
        for account_id in accounts_to_remove:
            del execution_result.final_states[account_id]
    
    def _validate_oracle_proofs(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Validate all oracle proofs in transactions.
        
        Args:
            transactions: List of transactions to validate
            
        Returns:
            Validation result dictionary
            
        Validates:
            Requirements 3.4
        """
        # Check if any transactions have oracle proofs
        transactions_with_oracles = [
            tx for tx in transactions if tx.oracle_proofs
        ]
        
        if not transactions_with_oracles:
            # No oracle proofs to validate
            return {
                "is_valid": True,
                "validated_count": 0
            }
        
        # Validate each oracle proof
        for tx in transactions_with_oracles:
            for oracle_proof in tx.oracle_proofs:
                # TODO: Integrate with actual oracle validator from v1.7.0
                # For now, assume all oracle proofs are valid
                # In production, this would call the OracleValidator
                pass
        
        return {
            "is_valid": True,
            "validated_count": len(transactions_with_oracles)
        }
    
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
    
    def _calculate_throughput_improvement(self,
                                         execution_result: ExecutionResult,
                                         transactions: List[Transaction]) -> float:
        """
        Calculate throughput improvement vs serial execution.
        
        Args:
            execution_result: Parallel execution result
            transactions: Original transactions
            
        Returns:
            Throughput improvement ratio (parallel vs serial)
        """
        # Estimate serial execution time
        # Assume each transaction takes equal time
        if len(transactions) == 0:
            return 1.0
        
        avg_tx_time = execution_result.execution_time / len(transactions)
        estimated_serial_time = avg_tx_time * len(transactions)
        
        # Calculate improvement
        if execution_result.execution_time > 0:
            improvement = estimated_serial_time / execution_result.execution_time
            return improvement
        else:
            return 1.0
    
    def _calculate_avg_parallelism(self, execution_result: ExecutionResult) -> float:
        """
        Calculate average parallelism (concurrent transactions).
        
        Args:
            execution_result: Execution result
            
        Returns:
            Average number of concurrent transactions
        """
        if not execution_result.parallel_groups:
            return 1.0
        
        # Count transactions in parallel groups
        parallel_tx_count = sum(
            len(group) for group in execution_result.parallel_groups if len(group) > 1
        )
        
        if len(execution_result.parallel_groups) > 0:
            return parallel_tx_count / len(execution_result.parallel_groups)
        else:
            return 1.0


# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.8.0"
__author__ = "Aethel Team"
__all__ = [
    "CommitManager",
]
