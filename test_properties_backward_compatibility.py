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
Property-Based Tests for Diotec360 v1.8.0 Backward Compatibility

Uses Hypothesis to generate random test cases and verify that single
transaction execution maintains identical behavior to v1.7.0.

Author: Diotec360 Team
Version: 1.8.0
Date: February 4, 2026
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import time
from diotec360.core.synchrony import Transaction, BatchResult
from diotec360.core.batch_processor import BatchProcessor


# ============================================================================
# STRATEGIES
# ============================================================================

@st.composite
def transaction_strategy(draw):
    """Generate random Transaction objects"""
    tx_id = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    intent_name = draw(st.sampled_from(['transfer', 'check_balance', 'deposit', 'withdraw']))
    
    # Generate accounts
    num_accounts = draw(st.integers(min_value=0, max_value=5))
    accounts = {}
    for i in range(num_accounts):
        account_id = f"account_{i}"
        balance = draw(st.integers(min_value=0, max_value=10000))
        accounts[account_id] = {"balance": balance}
    
    # Generate operations
    num_operations = draw(st.integers(min_value=0, max_value=10))
    operations = []
    for _ in range(num_operations):
        op_type = draw(st.sampled_from(['debit', 'credit', 'check']))
        if accounts:
            account = draw(st.sampled_from(list(accounts.keys())))
            amount = draw(st.integers(min_value=1, max_value=100))
            operations.append({
                "type": op_type,
                "account": account,
                "amount": amount
            })
    
    # Generate verify conditions
    num_conditions = draw(st.integers(min_value=0, max_value=3))
    verify_conditions = []
    for _ in range(num_conditions):
        if accounts:
            account = draw(st.sampled_from(list(accounts.keys())))
            verify_conditions.append(f"{account}.balance >= 0")
    
    return Transaction(
        id=tx_id,
        intent_name=intent_name,
        accounts=accounts,
        operations=operations,
        verify_conditions=verify_conditions
    )


# ============================================================================
# PROPERTY 20: SINGLE TRANSACTION BACKWARD COMPATIBILITY
# ============================================================================

@settings(max_examples=100, deadline=5000)
@given(tx=transaction_strategy())
def test_property_20_single_transaction_backward_compatibility(tx):
    """
    Feature: synchrony-protocol, Property 20: Single Transaction Backward Compatibility
    
    Validates: Requirements 8.1, 8.3
    
    Property: For any single transaction T:
        execute_single_transaction(T) ≡ execute_batch([T])
    
    This ensures that the new execute_single_transaction method
    produces identical results to the batch execution method,
    maintaining backward compatibility with v1.7.0.
    """
    processor = BatchProcessor()
    
    # Execute via single transaction method
    result_single = processor.execute_single_transaction(tx)
    
    # Execute via batch method
    result_batch = processor.execute_batch([tx])
    
    # Results should be equivalent
    assert result_single.success == result_batch.success, \
        "Success status should match"
    
    assert result_single.transactions_executed == result_batch.transactions_executed, \
        "Transaction count should match"
    
    # Both should execute exactly 1 transaction
    if result_single.success:
        assert result_single.transactions_executed == 1, \
            "Should execute exactly 1 transaction"
        assert result_batch.transactions_executed == 1, \
            "Should execute exactly 1 transaction"
    
    # Execution time should be similar (within 10x)
    if result_single.execution_time > 0 and result_batch.execution_time > 0:
        time_ratio = result_single.execution_time / result_batch.execution_time
        assert 0.1 <= time_ratio <= 10.0, \
            f"Execution times should be similar (ratio: {time_ratio})"


# ============================================================================
# PROPERTY 21: API CONTRACT PRESERVATION
# ============================================================================

@settings(max_examples=100, deadline=5000)
@given(tx=transaction_strategy())
def test_property_21_api_contract_preservation(tx):
    """
    Feature: synchrony-protocol, Property 21: API Contract Preservation
    
    Validates: Requirements 8.4
    
    Property: For any single transaction T:
        1. execute_single_transaction accepts Transaction object
        2. execute_single_transaction returns BatchResult object
        3. BatchResult contains all required fields from v1.7.0
        4. Field types match v1.7.0 specification
    
    This ensures that the API contract from v1.7.0 is preserved,
    allowing existing code to work without modification.
    """
    processor = BatchProcessor()
    
    # Execute transaction
    result = processor.execute_single_transaction(tx)
    
    # Verify return type
    assert isinstance(result, BatchResult), \
        "Result must be BatchResult instance"
    
    # Verify required fields exist
    required_fields = [
        'success',
        'transactions_executed',
        'transactions_parallel',
        'execution_time',
        'throughput_improvement'
    ]
    
    for field in required_fields:
        assert hasattr(result, field), \
            f"Result must have '{field}' field (v1.7.0 compatibility)"
    
    # Verify field types
    assert isinstance(result.success, bool), \
        "success must be bool"
    
    assert isinstance(result.transactions_executed, int), \
        "transactions_executed must be int"
    
    assert isinstance(result.transactions_parallel, int), \
        "transactions_parallel must be int"
    
    assert isinstance(result.execution_time, float), \
        "execution_time must be float"
    
    assert isinstance(result.throughput_improvement, float), \
        "throughput_improvement must be float"
    
    # Verify value constraints
    assert result.transactions_executed >= 0, \
        "transactions_executed must be non-negative"
    
    assert result.transactions_parallel >= 0, \
        "transactions_parallel must be non-negative"
    
    assert result.execution_time >= 0, \
        "execution_time must be non-negative"
    
    assert result.throughput_improvement >= 0, \
        "throughput_improvement must be non-negative"


# ============================================================================
# PROPERTY 22: TRANSACTION ID PRESERVATION
# ============================================================================

@settings(max_examples=50, deadline=5000)
@given(tx=transaction_strategy())
def test_property_22_transaction_id_preservation(tx):
    """
    Feature: synchrony-protocol, Property 22: Transaction ID Preservation
    
    Property: Transaction IDs are preserved through execution
    
    This ensures that transaction tracking and debugging
    capabilities from v1.7.0 are maintained.
    """
    processor = BatchProcessor()
    
    # Store original ID
    original_id = tx.id
    
    # Execute transaction
    result = processor.execute_single_transaction(tx)
    
    # Transaction ID should be unchanged
    assert tx.id == original_id, \
        "Transaction ID should not be modified during execution"
    
    # If successful, should have executed 1 transaction
    if result.success:
        assert result.transactions_executed == 1, \
            "Should execute exactly 1 transaction"


# ============================================================================
# PROPERTY 23: DETERMINISTIC EXECUTION
# ============================================================================

@settings(max_examples=50, deadline=5000)
@given(tx=transaction_strategy())
def test_property_23_deterministic_execution(tx):
    """
    Feature: synchrony-protocol, Property 23: Deterministic Execution
    
    Property: Executing the same transaction multiple times
    produces the same result (success/failure status)
    
    This ensures deterministic behavior, a core guarantee
    from v1.7.0.
    """
    processor = BatchProcessor()
    
    # Execute transaction twice
    result1 = processor.execute_single_transaction(tx)
    result2 = processor.execute_single_transaction(tx)
    
    # Results should be identical
    assert result1.success == result2.success, \
        "Execution should be deterministic"
    
    assert result1.transactions_executed == result2.transactions_executed, \
        "Transaction count should be deterministic"


# ============================================================================
# PROPERTY 24: EMPTY TRANSACTION HANDLING
# ============================================================================

@settings(max_examples=20, deadline=5000)
@given(
    tx_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    intent_name=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))
)
def test_property_24_empty_transaction_handling(tx_id, intent_name):
    """
    Feature: synchrony-protocol, Property 24: Empty Transaction Handling
    
    Property: Transactions with no accounts or operations
    should execute successfully without errors
    
    This ensures robustness for edge cases.
    """
    processor = BatchProcessor()
    
    # Create empty transaction
    tx = Transaction(
        id=tx_id,
        intent_name=intent_name,
        accounts={},
        operations=[],
        verify_conditions=[]
    )
    
    # Execute transaction
    result = processor.execute_single_transaction(tx)
    
    # Should not raise exception
    assert isinstance(result, BatchResult), \
        "Empty transaction should return BatchResult"
    
    # Should succeed (no operations = no failures)
    assert result.success is True, \
        "Empty transaction should succeed"
    
    assert result.transactions_executed == 1, \
        "Should count as 1 executed transaction"


# ============================================================================
# PROPERTY 25: EXECUTION TIME BOUNDS
# ============================================================================

@settings(max_examples=50, deadline=5000)
@given(tx=transaction_strategy())
def test_property_25_execution_time_bounds(tx):
    """
    Feature: synchrony-protocol, Property 25: Execution Time Bounds
    
    Property: Single transaction execution completes within
    reasonable time bounds (< 5 seconds for simple transactions)
    
    This ensures performance characteristics are maintained.
    """
    processor = BatchProcessor()
    
    # Execute transaction
    start_time = time.time()
    result = processor.execute_single_transaction(tx)
    wall_time = time.time() - start_time
    
    # Should complete quickly
    assert wall_time < 5.0, \
        f"Single transaction should complete in < 5s (took {wall_time:.2f}s)"
    
    # Recorded execution time should be reasonable
    assert result.execution_time < 5.0, \
        f"Recorded execution time should be < 5s (was {result.execution_time:.2f}s)"
    
    # Recorded time should be close to wall time (within 2x)
    if result.execution_time > 0:
        time_ratio = wall_time / result.execution_time
        assert 0.5 <= time_ratio <= 2.0, \
            f"Recorded time should match wall time (ratio: {time_ratio:.2f})"


def run_all_property_tests():
    """Run all property tests"""
    print("\n" + "="*70)
    print("🧪 Diotec360 v1.8.0 - BACKWARD COMPATIBILITY PROPERTY TESTS")
    print("="*70 + "\n")
    
    test_functions = [
        test_property_20_single_transaction_backward_compatibility,
        test_property_21_api_contract_preservation,
        test_property_22_transaction_id_preservation,
        test_property_23_deterministic_execution,
        test_property_24_empty_transaction_handling,
        test_property_25_execution_time_bounds
    ]
    
    total_tests = len(test_functions)
    passed_tests = 0
    
    for test_func in test_functions:
        print(f"\n📋 {test_func.__name__}")
        print("-" * 70)
        
        try:
            test_func()
            passed_tests += 1
            print(f"✅ PASSED")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print("\n" + "="*70)
    print(f"📊 RESULTS: {passed_tests}/{total_tests} property tests passed")
    
    if passed_tests == total_tests:
        print("✅ ALL PROPERTY TESTS PASSED")
    else:
        print(f"❌ {total_tests - passed_tests} tests failed")
    
    print("="*70 + "\n")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_property_tests()
    exit(0 if success else 1)
