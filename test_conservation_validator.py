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
Unit Tests for Conservation Validator - Synchrony Protocol v1.8.0

Tests the conservation validator that ensures global conservation
across transaction batches.

Author: Diotec360 Team
Version: 1.8.0
Date: February 4, 2026
"""

import pytest
from diotec360.core.conservation_validator import ConservationValidator
from diotec360.core.synchrony import Transaction, ExecutionResult, ExecutionEvent, EventType


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def validator():
    """Create a conservation validator"""
    return ConservationValidator(timeout_seconds=30)


# ============================================================================
# UNIT TESTS - Task 8.3
# ============================================================================

def test_batch_with_balanced_transfers(validator):
    """
    Test batch with balanced transfers (conservation holds).
    
    Validates: Task 8.3 - Balanced transfers
    """
    # Initial states: Alice=100, Bob=50
    initial_states = {
        "Alice": {"balance": 100},
        "Bob": {"balance": 50}
    }
    
    # Final states: Alice=80, Bob=70 (Alice sent 20 to Bob)
    execution_result = ExecutionResult(
        final_states={
            "Alice": {"balance": 80},
            "Bob": {"balance": 70}
        },
        execution_trace=[
            ExecutionEvent(1.0, "T1", EventType.START, thread_id=0),
            ExecutionEvent(1.5, "T1", EventType.COMMIT, thread_id=0)
        ],
        parallel_groups=[{"T1"}],
        execution_time=0.5,
        thread_count=1
    )
    
    result = validator.validate_batch_conservation(execution_result, initial_states)
    
    # Should pass conservation
    assert result.is_valid is True
    assert result.violation_amount is None


def test_batch_with_conservation_violation(validator):
    """
    Test batch with conservation violation (money created).
    
    Validates: Task 8.3 - Conservation violation
    """
    # Initial states: Alice=100, Bob=50
    initial_states = {
        "Alice": {"balance": 100},
        "Bob": {"balance": 50}
    }
    
    # Final states: Alice=100, Bob=100 (50 units created!)
    execution_result = ExecutionResult(
        final_states={
            "Alice": {"balance": 100},
            "Bob": {"balance": 100}
        },
        execution_trace=[
            ExecutionEvent(1.0, "T1", EventType.START, thread_id=0),
            ExecutionEvent(1.5, "T1", EventType.COMMIT, thread_id=0)
        ],
        parallel_groups=[{"T1"}],
        execution_time=0.5,
        thread_count=1
    )
    
    result = validator.validate_batch_conservation(execution_result, initial_states)
    
    # Should fail conservation
    assert result.is_valid is False
    assert result.violation_amount == 50  # 50 units created
    assert "violated" in result.error_message.lower()


def test_empty_batch(validator):
    """
    Test empty batch (no transactions).
    
    Validates: Task 8.3 - Empty batch
    """
    # Initial states: Alice=100
    initial_states = {
        "Alice": {"balance": 100}
    }
    
    # Final states: Alice=100 (no change)
    execution_result = ExecutionResult(
        final_states={
            "Alice": {"balance": 100}
        },
        execution_trace=[],
        parallel_groups=[],
        execution_time=0.0,
        thread_count=0
    )
    
    result = validator.validate_batch_conservation(execution_result, initial_states)
    
    # Should pass conservation
    assert result.is_valid is True


def test_multiple_accounts_balanced(validator):
    """
    Test batch with multiple accounts, all balanced.
    
    Validates: Property 8 - Conservation Across Batch
    """
    # Initial: A=100, B=50, C=75, D=25 (total=250)
    initial_states = {
        "A": {"balance": 100},
        "B": {"balance": 50},
        "C": {"balance": 75},
        "D": {"balance": 25}
    }
    
    # Final: A=80, B=70, C=60, D=40 (total=250)
    # A sent 20 to B, C sent 15 to D
    execution_result = ExecutionResult(
        final_states={
            "A": {"balance": 80},
            "B": {"balance": 70},
            "C": {"balance": 60},
            "D": {"balance": 40}
        },
        execution_trace=[
            ExecutionEvent(1.0, "T1", EventType.START, thread_id=0),
            ExecutionEvent(1.0, "T2", EventType.START, thread_id=1),
            ExecutionEvent(1.5, "T1", EventType.COMMIT, thread_id=0),
            ExecutionEvent(1.6, "T2", EventType.COMMIT, thread_id=1)
        ],
        parallel_groups=[{"T1", "T2"}],
        execution_time=0.6,
        thread_count=2
    )
    
    result = validator.validate_batch_conservation(execution_result, initial_states)
    
    # Should pass conservation
    assert result.is_valid is True


def test_prove_conservation_invariant_valid(validator):
    """
    Test Z3 proof generation for valid conservation.
    
    Validates: Requirements 3.3
    """
    transactions = [
        Transaction(
            id="T1",
            intent_name="transfer",
            accounts={"Alice": {}, "Bob": {}},
            operations=[],
            verify_conditions=[]
        )
    ]
    
    initial_states = {
        "Alice": {"balance": 100},
        "Bob": {"balance": 50}
    }
    
    proof_result = validator.prove_conservation_invariant(transactions, initial_states)
    
    # Should generate proof
    assert proof_result.is_linearizable is True  # Reused field
    assert proof_result.proof is not None
    assert "CONSERVATION PROOF" in proof_result.proof


def test_new_account_creation(validator):
    """
    Test batch where new account is created (with zero balance).
    
    Validates: Edge case - new accounts
    """
    # Initial: Alice=100
    initial_states = {
        "Alice": {"balance": 100}
    }
    
    # Final: Alice=80, Bob=20 (Bob is new account)
    execution_result = ExecutionResult(
        final_states={
            "Alice": {"balance": 80},
            "Bob": {"balance": 20}
        },
        execution_trace=[
            ExecutionEvent(1.0, "T1", EventType.START, thread_id=0),
            ExecutionEvent(1.5, "T1", EventType.COMMIT, thread_id=0)
        ],
        parallel_groups=[{"T1"}],
        execution_time=0.5,
        thread_count=1
    )
    
    result = validator.validate_batch_conservation(execution_result, initial_states)
    
    # Should pass conservation (Alice sent 20 to new account Bob)
    assert result.is_valid is True


def test_floating_point_precision(validator):
    """
    Test conservation with floating point balances.
    
    Validates: Edge case - floating point precision
    """
    # Initial: Alice=100.5, Bob=50.3
    initial_states = {
        "Alice": {"balance": 100.5},
        "Bob": {"balance": 50.3}
    }
    
    # Final: Alice=80.5, Bob=70.3 (Alice sent 20.0 to Bob)
    execution_result = ExecutionResult(
        final_states={
            "Alice": {"balance": 80.5},
            "Bob": {"balance": 70.3}
        },
        execution_trace=[
            ExecutionEvent(1.0, "T1", EventType.START, thread_id=0),
            ExecutionEvent(1.5, "T1", EventType.COMMIT, thread_id=0)
        ],
        parallel_groups=[{"T1"}],
        execution_time=0.5,
        thread_count=1
    )
    
    result = validator.validate_batch_conservation(execution_result, initial_states)
    
    # Should pass conservation (within epsilon)
    assert result.is_valid is True


# ============================================================================
# PROPERTY TEST - Task 8.2
# ============================================================================

def test_property_conservation_across_batch(validator):
    """
    Feature: synchrony-protocol, Property 8: Conservation Across Batch
    
    For any batch execution, the sum of all account balances before the batch
    SHALL equal the sum of all account balances after the batch.
    
    Validates: Requirements 3.3
    """
    # Test with various batch sizes
    test_cases = [
        # (initial_states, final_states, should_pass)
        (
            {"A": {"balance": 100}},
            {"A": {"balance": 100}},
            True  # No change
        ),
        (
            {"A": {"balance": 100}, "B": {"balance": 50}},
            {"A": {"balance": 80}, "B": {"balance": 70}},
            True  # Balanced transfer
        ),
        (
            {"A": {"balance": 100}, "B": {"balance": 50}},
            {"A": {"balance": 100}, "B": {"balance": 100}},
            False  # Money created
        ),
        (
            {"A": {"balance": 100}, "B": {"balance": 50}, "C": {"balance": 75}},
            {"A": {"balance": 90}, "B": {"balance": 60}, "C": {"balance": 75}},
            True  # Balanced multi-party
        ),
    ]
    
    for initial, final, should_pass in test_cases:
        execution_result = ExecutionResult(
            final_states=final,
            execution_trace=[],
            parallel_groups=[],
            execution_time=0.0,
            thread_count=1
        )
        
        result = validator.validate_batch_conservation(execution_result, initial)
        
        assert result.is_valid == should_pass, \
            f"Conservation check failed for initial={initial}, final={final}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
