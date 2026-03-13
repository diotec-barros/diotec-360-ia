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
Unit Tests for Commit Manager - Synchrony Protocol v1.8.0

Tests atomic commit/rollback functionality with comprehensive validation.

Author: Diotec360 Team
Version: 1.8.0
Date: February 4, 2026
"""

import pytest
import time
from typing import Dict, List, Any

from diotec360.core.commit_manager import CommitManager
from diotec360.core.synchrony import (
    Transaction,
    ExecutionResult,
    ExecutionEvent,
    ProofResult,
    EventType,
    LinearizabilityError,
    ConservationViolationError,
    OracleValidationError
)
from diotec360.core.conservation import ConservationResult


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def commit_manager():
    """Create CommitManager instance"""
    return CommitManager()


@pytest.fixture
def simple_transactions():
    """Create simple test transactions"""
    return [
        Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={"alice": {"balance": 100}, "bob": {"balance": 50}},
            operations=[],
            verify_conditions=[],
            oracle_proofs=[]
        ),
        Transaction(
            id="tx2",
            intent_name="transfer",
            accounts={"charlie": {"balance": 75}, "dave": {"balance": 25}},
            operations=[],
            verify_conditions=[],
            oracle_proofs=[]
        )
    ]


@pytest.fixture
def initial_states():
    """Create initial account states"""
    return {
        "alice": {"balance": 100},
        "bob": {"balance": 50},
        "charlie": {"balance": 75},
        "dave": {"balance": 25}
    }


@pytest.fixture
def successful_execution_result():
    """Create successful execution result"""
    return ExecutionResult(
        final_states={
            "alice": {"balance": 90},
            "bob": {"balance": 60},
            "charlie": {"balance": 65},
            "dave": {"balance": 35}
        },
        execution_trace=[
            ExecutionEvent(
                timestamp=0.0,
                transaction_id="tx1",
                event_type=EventType.START,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=0.1,
                transaction_id="tx2",
                event_type=EventType.START,
                thread_id=1
            ),
            ExecutionEvent(
                timestamp=0.2,
                transaction_id="tx1",
                event_type=EventType.COMMIT,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=0.3,
                transaction_id="tx2",
                event_type=EventType.COMMIT,
                thread_id=1
            )
        ],
        parallel_groups=[{"tx1", "tx2"}],
        execution_time=0.3,
        thread_count=2
    )


@pytest.fixture
def valid_proof_result():
    """Create valid linearizability proof"""
    return ProofResult(
        is_linearizable=True,
        serial_order=["tx1", "tx2"],
        proof="Valid linearizability proof",
        counterexample=None,
        proof_time=0.1
    )


@pytest.fixture
def invalid_proof_result():
    """Create invalid linearizability proof"""
    return ProofResult(
        is_linearizable=False,
        serial_order=None,
        proof=None,
        counterexample={"error": "No valid serial order"},
        proof_time=0.1
    )


@pytest.fixture
def valid_conservation_result():
    """Create valid conservation result"""
    return ConservationResult(
        is_valid=True,
        changes=[],
        violation_amount=None,
        error_message=None
    )


@pytest.fixture
def invalid_conservation_result():
    """Create invalid conservation result"""
    return ConservationResult(
        is_valid=False,
        changes=[],
        violation_amount=10.0,
        error_message="Conservation violated: sum changed by 10"
    )


# ============================================================================
# TEST: Successful Commit
# ============================================================================

def test_successful_commit(commit_manager,
                          simple_transactions,
                          initial_states,
                          successful_execution_result,
                          valid_proof_result,
                          valid_conservation_result):
    """
    Test successful batch commit with all validations passing.
    
    Validates:
        Requirements 3.1, 3.2, 3.5
    """
    # Execute commit
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=valid_proof_result,
        conservation_result=valid_conservation_result
    )
    
    # Verify success
    assert result.success is True
    assert result.transactions_executed == 2
    assert result.error_message is None
    assert result.error_type is None
    
    # Verify proofs included
    assert result.linearizability_proof is not None
    assert result.linearizability_proof.is_linearizable is True
    assert result.conservation_proof is not None
    assert result.conservation_proof.is_valid is True
    
    # Verify execution details
    assert result.execution_trace == successful_execution_result.execution_trace
    assert result.parallel_groups == successful_execution_result.parallel_groups
    assert result.thread_count == 2
    
    # Verify performance metrics
    assert result.throughput_improvement > 0
    assert result.avg_parallelism > 0


# ============================================================================
# TEST: Rollback on Linearizability Failure
# ============================================================================

def test_rollback_on_linearizability_failure(commit_manager,
                                             simple_transactions,
                                             initial_states,
                                             successful_execution_result,
                                             invalid_proof_result,
                                             valid_conservation_result):
    """
    Test rollback when linearizability proof fails.
    
    Validates:
        Requirements 3.1, 3.2
    """
    # Store original final states
    original_final_states = successful_execution_result.final_states.copy()
    
    # Execute commit (should fail and rollback)
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=invalid_proof_result,
        conservation_result=valid_conservation_result
    )
    
    # Verify failure
    assert result.success is False
    assert result.transactions_executed == 0  # None committed
    assert result.error_type == "LinearizabilityError"
    assert result.error_message is not None
    
    # Verify rollback occurred
    # Final states should be restored to initial states
    for account_id, initial_state in initial_states.items():
        assert successful_execution_result.final_states[account_id] == initial_state
    
    # Verify diagnostic info
    assert result.diagnostic_info is not None
    assert "error_type" in result.diagnostic_info


# ============================================================================
# TEST: Rollback on Conservation Violation
# ============================================================================

def test_rollback_on_conservation_violation(commit_manager,
                                           simple_transactions,
                                           initial_states,
                                           successful_execution_result,
                                           valid_proof_result,
                                           invalid_conservation_result):
    """
    Test rollback when conservation is violated.
    
    Validates:
        Requirements 3.1, 3.2
    """
    # Modify final states to violate conservation
    successful_execution_result.final_states["alice"]["balance"] = 1000  # Money created!
    
    # Execute commit (should fail and rollback)
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=valid_proof_result,
        conservation_result=invalid_conservation_result
    )
    
    # Verify failure
    assert result.success is False
    assert result.transactions_executed == 0
    assert result.error_type == "ConservationViolationError"
    assert "conservation" in result.error_message.lower()
    
    # Verify rollback occurred
    for account_id, initial_state in initial_states.items():
        assert successful_execution_result.final_states[account_id] == initial_state


# ============================================================================
# TEST: Rollback Restores Initial States
# ============================================================================

def test_rollback_restores_initial_states(commit_manager,
                                         successful_execution_result,
                                         initial_states):
    """
    Test that rollback correctly restores all initial states.
    
    Validates:
        Requirements 3.1, 3.2
    """
    # Store original final states
    modified_states = {
        "alice": {"balance": 90},
        "bob": {"balance": 60},
        "charlie": {"balance": 65},
        "dave": {"balance": 35}
    }
    successful_execution_result.final_states = modified_states.copy()
    
    # Execute rollback
    commit_manager.rollback_batch(
        execution_result=successful_execution_result,
        initial_states=initial_states
    )
    
    # Verify all states restored
    assert successful_execution_result.final_states == initial_states


# ============================================================================
# TEST: Rollback Removes New Accounts
# ============================================================================

def test_rollback_removes_new_accounts(commit_manager,
                                      successful_execution_result,
                                      initial_states):
    """
    Test that rollback removes accounts created during batch.
    
    Validates:
        Requirements 3.1, 3.2
    """
    # Add a new account that didn't exist initially
    successful_execution_result.final_states["eve"] = {"balance": 100}
    
    # Execute rollback
    commit_manager.rollback_batch(
        execution_result=successful_execution_result,
        initial_states=initial_states
    )
    
    # Verify new account removed
    assert "eve" not in successful_execution_result.final_states
    
    # Verify original accounts restored
    assert successful_execution_result.final_states == initial_states


# ============================================================================
# TEST: Oracle Validation
# ============================================================================

def test_oracle_validation_with_no_oracles(commit_manager,
                                          simple_transactions,
                                          initial_states,
                                          successful_execution_result,
                                          valid_proof_result,
                                          valid_conservation_result):
    """
    Test oracle validation when no oracle proofs present.
    
    Validates:
        Requirements 3.4
    """
    # Ensure no oracle proofs
    for tx in simple_transactions:
        tx.oracle_proofs = []
    
    # Execute commit
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=valid_proof_result,
        conservation_result=valid_conservation_result
    )
    
    # Should succeed (no oracles to validate)
    assert result.success is True


def test_oracle_validation_with_oracles(commit_manager,
                                       simple_transactions,
                                       initial_states,
                                       successful_execution_result,
                                       valid_proof_result,
                                       valid_conservation_result):
    """
    Test oracle validation when oracle proofs present.
    
    Validates:
        Requirements 3.4
    """
    # Add oracle proofs to transactions
    simple_transactions[0].oracle_proofs = [{"oracle_id": "price_feed", "value": 100}]
    
    # Execute commit
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=valid_proof_result,
        conservation_result=valid_conservation_result
    )
    
    # Should succeed (oracle validation passes)
    assert result.success is True


# ============================================================================
# TEST: Performance Metrics
# ============================================================================

def test_throughput_improvement_calculation(commit_manager,
                                           simple_transactions,
                                           initial_states,
                                           successful_execution_result,
                                           valid_proof_result,
                                           valid_conservation_result):
    """
    Test throughput improvement calculation.
    
    Validates:
        Requirements 7.1, 7.2
    """
    # Execute commit
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=valid_proof_result,
        conservation_result=valid_conservation_result
    )
    
    # Verify throughput improvement calculated
    assert result.throughput_improvement > 0
    assert isinstance(result.throughput_improvement, float)


def test_avg_parallelism_calculation(commit_manager,
                                    simple_transactions,
                                    initial_states,
                                    successful_execution_result,
                                    valid_proof_result,
                                    valid_conservation_result):
    """
    Test average parallelism calculation.
    
    Validates:
        Requirements 7.3
    """
    # Execute commit
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=valid_proof_result,
        conservation_result=valid_conservation_result
    )
    
    # Verify avg parallelism calculated
    assert result.avg_parallelism > 0
    assert isinstance(result.avg_parallelism, float)


# ============================================================================
# TEST: Empty Batch
# ============================================================================

def test_empty_batch_commit(commit_manager):
    """
    Test commit with empty batch.
    
    Validates:
        Requirements 3.1, 3.2
    """
    # Create empty execution result
    execution_result = ExecutionResult(
        final_states={},
        execution_trace=[],
        parallel_groups=[],
        execution_time=0.0,
        thread_count=0
    )
    
    proof_result = ProofResult(
        is_linearizable=True,
        serial_order=[],
        proof="Empty batch proof",
        counterexample=None,
        proof_time=0.0
    )
    
    conservation_result = ConservationResult(
        is_valid=True,
        changes=[],
        violation_amount=None,
        error_message=None
    )
    
    # Execute commit
    result = commit_manager.commit_batch(
        execution_result=execution_result,
        transactions=[],
        initial_states={},
        proof_result=proof_result,
        conservation_result=conservation_result
    )
    
    # Should succeed
    assert result.success is True
    assert result.transactions_executed == 0


# ============================================================================
# TEST: Auto-generate Proofs
# ============================================================================

def test_auto_generate_linearizability_proof(commit_manager,
                                            simple_transactions,
                                            initial_states,
                                            successful_execution_result,
                                            valid_conservation_result):
    """
    Test auto-generation of linearizability proof when not provided.
    
    Validates:
        Requirements 4.1
    """
    # Don't provide proof_result - should auto-generate
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=None,  # Auto-generate
        conservation_result=valid_conservation_result
    )
    
    # Verify proof was generated
    assert result.linearizability_proof is not None


def test_auto_validate_conservation(commit_manager,
                                   simple_transactions,
                                   initial_states,
                                   successful_execution_result,
                                   valid_proof_result):
    """
    Test auto-validation of conservation when not provided.
    
    Validates:
        Requirements 3.3
    """
    # Don't provide conservation_result - should auto-validate
    result = commit_manager.commit_batch(
        execution_result=successful_execution_result,
        transactions=simple_transactions,
        initial_states=initial_states,
        proof_result=valid_proof_result,
        conservation_result=None  # Auto-validate
    )
    
    # Verify conservation was validated
    assert result.conservation_proof is not None


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
