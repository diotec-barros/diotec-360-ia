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
Unit Tests for Linearizability Prover - Synchrony Protocol v1.8.0

Tests the Z3-based linearizability prover that verifies parallel execution
is equivalent to some serial execution.

Author: Diotec360 Team
Version: 1.8.0
Date: February 4, 2026
"""

import pytest
import time
from typing import List, Dict, Set

from diotec360.core.linearizability_prover import LinearizabilityProver
from diotec360.core.synchrony import (
    Transaction,
    ExecutionResult,
    ExecutionEvent,
    ProofResult,
    EventType
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def prover():
    """Create a linearizability prover"""
    return LinearizabilityProver(timeout_seconds=30)


@pytest.fixture
def simple_transactions():
    """Create simple test transactions"""
    return [
        Transaction(
            id="T1",
            intent_name="transfer",
            accounts={"A": {}, "B": {}},
            operations=[],
            verify_conditions=[]
        ),
        Transaction(
            id="T2",
            intent_name="transfer",
            accounts={"C": {}, "D": {}},
            operations=[],
            verify_conditions=[]
        )
    ]


@pytest.fixture
def dependent_transactions():
    """Create transactions with dependencies"""
    return [
        Transaction(
            id="T1",
            intent_name="transfer",
            accounts={"A": {}, "B": {}},
            operations=[],
            verify_conditions=[]
        ),
        Transaction(
            id="T2",
            intent_name="transfer",
            accounts={"B": {}, "C": {}},  # Depends on T1 (reads B)
            operations=[],
            verify_conditions=[]
        )
    ]


@pytest.fixture
def simple_execution_result():
    """Create simple execution result"""
    return ExecutionResult(
        final_states={
            "A": {"balance": 100},
            "B": {"balance": 200},
            "C": {"balance": 300},
            "D": {"balance": 400}
        },
        execution_trace=[
            ExecutionEvent(
                timestamp=1.0,
                transaction_id="T1",
                event_type=EventType.START,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=1.1,
                transaction_id="T2",
                event_type=EventType.START,
                thread_id=1
            ),
            ExecutionEvent(
                timestamp=1.5,
                transaction_id="T1",
                event_type=EventType.COMMIT,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=1.6,
                transaction_id="T2",
                event_type=EventType.COMMIT,
                thread_id=1
            )
        ],
        parallel_groups=[{"T1", "T2"}],
        execution_time=0.6,
        thread_count=2
    )


# ============================================================================
# UNIT TESTS - Task 7.5
# ============================================================================

def test_encode_simple_2_transaction_batch(prover, simple_transactions, simple_execution_result):
    """
    Test encoding of simple 2-transaction batch.
    
    Validates: Task 7.5 - SMT encoding
    """
    constraints = prover.encode_execution(simple_execution_result, simple_transactions)
    
    # Should have constraints
    assert len(constraints) > 0


def test_encode_with_dependencies(prover, dependent_transactions):
    """
    Test encoding with dependencies.
    
    Validates: Task 7.5 - SMT encoding with dependencies
    """
    execution_result = ExecutionResult(
        final_states={
            "A": {"balance": 100},
            "B": {"balance": 200},
            "C": {"balance": 300}
        },
        execution_trace=[
            ExecutionEvent(
                timestamp=1.0,
                transaction_id="T1",
                event_type=EventType.START,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=1.5,
                transaction_id="T1",
                event_type=EventType.COMMIT,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=2.0,
                transaction_id="T2",
                event_type=EventType.START,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=2.5,
                transaction_id="T2",
                event_type=EventType.COMMIT,
                thread_id=0
            )
        ],
        parallel_groups=[{"T1"}, {"T2"}],
        execution_time=1.5,
        thread_count=1
    )
    
    constraints = prover.encode_execution(execution_result, dependent_transactions)
    
    # Should encode dependency: T1 must complete before T2 starts
    assert len(constraints) > 0


def test_encode_with_conflicts(prover):
    """
    Test encoding with conflicts.
    
    Validates: Task 7.5 - SMT encoding with conflicts
    """
    # Create transactions with write-write conflict
    transactions = [
        Transaction(
            id="T1",
            intent_name="transfer",
            accounts={"A": {}},
            operations=[],
            verify_conditions=[]
        ),
        Transaction(
            id="T2",
            intent_name="transfer",
            accounts={"A": {}},  # Both write to A
            operations=[],
            verify_conditions=[]
        )
    ]
    
    execution_result = ExecutionResult(
        final_states={"A": {"balance": 100}},
        execution_trace=[
            ExecutionEvent(
                timestamp=1.0,
                transaction_id="T1",
                event_type=EventType.START,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=1.5,
                transaction_id="T1",
                event_type=EventType.COMMIT,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=2.0,
                transaction_id="T2",
                event_type=EventType.START,
                thread_id=0
            ),
            ExecutionEvent(
                timestamp=2.5,
                transaction_id="T2",
                event_type=EventType.COMMIT,
                thread_id=0
            )
        ],
        parallel_groups=[{"T1"}, {"T2"}],
        execution_time=1.5,
        thread_count=1
    )
    
    constraints = prover.encode_execution(execution_result, transactions)
    
    # Should encode conflict resolution constraints
    assert len(constraints) > 0


def test_find_serial_order_independent(prover, simple_transactions, simple_execution_result):
    """
    Test finding serial order for independent transactions.
    
    Validates: Requirements 4.2
    """
    serial_order = prover.find_serial_order(simple_transactions, simple_execution_result)
    
    # Should find a valid serial order
    assert serial_order is not None
    assert len(serial_order) == 2
    assert set(serial_order) == {"T1", "T2"}


def test_prove_linearizability_success(prover, simple_transactions, simple_execution_result):
    """
    Test successful linearizability proof.
    
    Validates: Requirements 4.1, 4.2, 4.4
    """
    proof_result = prover.prove_linearizability(simple_execution_result, simple_transactions)
    
    # Should prove linearizability
    assert proof_result.is_linearizable is True
    assert proof_result.serial_order is not None
    assert proof_result.proof is not None
    assert proof_result.counterexample is None
    assert proof_result.proof_time > 0
    
    # Proof should contain key information
    assert "LINEARIZABILITY PROOF" in proof_result.proof
    assert "serial order" in proof_result.proof.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
